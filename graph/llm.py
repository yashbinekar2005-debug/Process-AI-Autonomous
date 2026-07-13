import os
import json
import time
import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from config import settings

logger = logging.getLogger("enterprise_agent.graph.llm")

class MockLLM:
    def __init__(self):
        logger.warning("Initializing MockLLM. No real LLM provider is available.")

    def invoke(self, messages, *args, **kwargs) -> AIMessage:
        prompt_repr = ""
        for m in messages:
            if hasattr(m, "content"):
                prompt_repr += f"\n{m.content}"
            else:
                prompt_repr += f"\n{str(m)}"

        prompt_lower = prompt_repr.lower()

        if "select one of" in prompt_lower or "next agent" in prompt_lower or "supervisor" in prompt_lower:
            if "research_output" in prompt_lower and "analysis_output" in prompt_lower:
                if "critic_score" not in prompt_lower:
                    return AIMessage(content="critic")
                elif "critic" in prompt_lower:
                    return AIMessage(content="action")
            if "research" not in prompt_lower or "research_output" not in prompt_lower or len(prompt_lower) < 500:
                return AIMessage(content="research")
            elif "analysis" not in prompt_lower or "analysis_output" not in prompt_lower:
                return AIMessage(content="analysis")
            elif "critic" not in prompt_lower:
                return AIMessage(content="critic")
            else:
                return AIMessage(content="action")

        if "research agent" in prompt_lower or "web_search" in prompt_lower:
            content = (
                "**RESEARCH FINDINGS**:\n"
                "1. Competitor SaaS pricing analysis: Competitor 'Alpha' charges $49/month. Competitor 'Beta' charges $79/month.\n"
                "2. Standard Customer Support SLA requires P1 issues to be resolved within 4 hours.\n"
                "3. Industry benchmark ticket resolution efficiency shows standard routing saves 30% overhead."
            )
            return AIMessage(content=content)

        if "analysis agent" in prompt_lower or "run code" in prompt_lower or "repl" in prompt_lower:
            content = (
                "**ANALYSIS SUMMARY**:\n"
                "- Statistical calculation: Based on Competitor Alpha ($49) and Beta ($79), the average competitor SaaS cost is $64/month.\n"
                "- Proposed Strategy: Set our automation baseline price at $59/month to remain competitive and capture market share.\n"
                "- Impact Analysis: This pricing model guarantees a projected 18% increase in conversion rates for the next quarter."
            )
            return AIMessage(content=content)

        if "critic agent" in prompt_lower or "evaluate" in prompt_lower or "critic_score" in prompt_lower:
            response_data = {
                "critic_score": 0.85,
                "requires_human": True,
                "explanation": "The research and analysis are high quality. The pricing strategy aligns with market data. Paused for human approval before executing DB and Slack notifications."
            }
            return AIMessage(content=json.dumps(response_data))

        if "action agent" in prompt_lower or "send_email" in prompt_lower or "slack" in prompt_lower:
            content = (
                "**ACTIONS EXECUTED**:\n"
                "- Simulated database entry: Added competitor intelligence records to table 'competitor_intel'.\n"
                "- Slack webhook notification dispatched: 'Competitor Intelligence alert - Pricing Strategy finalized at $59/month.'\n"
                "- Email alert queued to operations: 'Task Completed: Enterprise AI Triage task executed successfully.'"
            )
            return AIMessage(content=content)

        return AIMessage(content="Drafting response: Multi-agent execution step evaluated.")

def _create_ollama_llm():
    try:
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            temperature=0.1,
            num_predict=4096,
        )
        logger.info(f"Initialized Ollama LLM: {settings.OLLAMA_MODEL} @ {settings.OLLAMA_BASE_URL}")
        return llm
    except ImportError:
        logger.warning("langchain-ollama not installed. Cannot use Ollama.")
        return None
    except Exception as e:
        logger.warning(f"Failed to connect to Ollama at {settings.OLLAMA_BASE_URL}: {e}")
        return None

def _create_gemini_llm():
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=api_key,
            temperature=0.1
        )
        logger.info(f"Initialized Gemini LLM: {settings.GEMINI_MODEL}")
        return llm
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini: {e}")
        return None

def _create_groq_llm():
    api_key = settings.GROQ_API_KEY
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    try:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            groq_api_key=api_key,
            model=settings.GROQ_MODEL,
            temperature=0.1
        )
        logger.info(f"Initialized Groq LLM: {settings.GROQ_MODEL}")
        return llm
    except ImportError:
        logger.warning("langchain-groq not installed. Install with: pip install langchain-groq")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize Groq: {e}")
        return None

def _invoke_with_retry(llm, messages, max_retries=None, delay=None):
    max_retries = max_retries or settings.LLM_MAX_RETRIES
    delay = delay or settings.LLM_RETRY_DELAY
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return llm.invoke(messages)
        except Exception as e:
            last_error = e
            logger.warning(f"LLM call failed (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(delay * attempt)

    raise last_error

class FallbackLLM:
    def __init__(self):
        self.llms = []
        self._init_llms()

    def _init_llms(self):
        provider = settings.LLM_PROVIDER.lower()

        if provider == "ollama":
            ollama_llm = _create_ollama_llm()
            if ollama_llm:
                self.llms.append(("ollama", ollama_llm))
            groq_llm = _create_groq_llm()
            if groq_llm:
                self.llms.append(("groq", groq_llm))
            gemini_llm = _create_gemini_llm()
            if gemini_llm:
                self.llms.append(("gemini", gemini_llm))
        elif provider == "groq":
            groq_llm = _create_groq_llm()
            if groq_llm:
                self.llms.append(("groq", groq_llm))
            gemini_llm = _create_gemini_llm()
            if gemini_llm:
                self.llms.append(("gemini", gemini_llm))
            ollama_llm = _create_ollama_llm()
            if ollama_llm:
                self.llms.append(("ollama", ollama_llm))
        else:
            gemini_llm = _create_gemini_llm()
            if gemini_llm:
                self.llms.append(("gemini", gemini_llm))
            groq_llm = _create_groq_llm()
            if groq_llm:
                self.llms.append(("groq", groq_llm))
            ollama_llm = _create_ollama_llm()
            if ollama_llm:
                self.llms.append(("ollama", ollama_llm))

        if not self.llms:
            logger.warning("No real LLM available. Will use MockLLM.")

    def invoke(self, messages, *args, **kwargs) -> AIMessage:
        for name, llm in self.llms:
            try:
                logger.debug(f"Attempting LLM call via {name}")
                return _invoke_with_retry(llm, messages)
            except Exception as e:
                logger.warning(f"{name} failed entirely: {e}. Trying next fallback...")

        logger.warning("All LLM providers failed. Falling back to MockLLM.")
        return MockLLM().invoke(messages)

_fallback_llm_instance = None

def get_llm():
    global _fallback_llm_instance
    if _fallback_llm_instance is None:
        _fallback_llm_instance = FallbackLLM()
    return _fallback_llm_instance

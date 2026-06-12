import os
import json
import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings

logger = logging.getLogger("enterprise_agent.graph.llm")

class MockLLM:
    """
    A smart mock LLM that returns contextual responses based on prompt inspection.
    This allows running the entire multi-agent graph, backend, and dashboard
    without needing a valid Gemini API key immediately.
    """
    def __init__(self):
        logger.warning("Initializing MockLLM. GEMINI_API_KEY is not configured.")

    def invoke(self, messages, *args, **kwargs) -> AIMessage:
        # Convert messages to a single string representation
        prompt_repr = ""
        for m in messages:
            if hasattr(m, "content"):
                prompt_repr += f"\n{m.content}"
            else:
                prompt_repr += f"\n{str(m)}"
        
        prompt_lower = prompt_repr.lower()
        
        # 1. Routing / Supervisor prompt check
        if "select one of" in prompt_lower or "next agent" in prompt_lower or "supervisor" in prompt_lower:
            # Let's inspect messages to decide the next agent
            if "research_output" in prompt_lower and "analysis_output" in prompt_lower:
                # If both research and analysis are done, go to action or critic
                if "critic_score" not in prompt_lower:
                    return AIMessage(content="critic")
                elif "critic" in prompt_lower:
                    return AIMessage(content="action")
            # Default sequence: research -> analysis -> critic -> action -> END
            if "research" not in prompt_lower or "research_output" not in prompt_lower or len(prompt_lower) < 500:
                return AIMessage(content="research")
            elif "analysis" not in prompt_lower or "analysis_output" not in prompt_lower:
                return AIMessage(content="analysis")
            elif "critic" not in prompt_lower:
                return AIMessage(content="critic")
            else:
                return AIMessage(content="action")

        # 2. Research Agent prompt check
        if "research agent" in prompt_lower or "web_search" in prompt_lower:
            content = (
                "**RESEARCH FINDINGS**:\n"
                "1. Competitor SaaS pricing analysis: Competitor 'Alpha' charges $49/month. Competitor 'Beta' charges $79/month.\n"
                "2. Standard Customer Support SLA requires P1 issues to be resolved within 4 hours.\n"
                "3. Industry benchmark ticket resolution efficiency shows standard routing saves 30% overhead."
            )
            return AIMessage(content=content)

        # 3. Analysis Agent prompt check
        if "analysis agent" in prompt_lower or "run code" in prompt_lower or "repl" in prompt_lower:
            content = (
                "**ANALYSIS SUMMARY**:\n"
                "- Statistical calculation: Based on Competitor Alpha ($49) and Beta ($79), the average competitor SaaS cost is $64/month.\n"
                "- Proposed Strategy: Set our automation baseline price at $59/month to remain competitive and capture market share.\n"
                "- Impact Analysis: This pricing model guarantees a projected 18% increase in conversion rates for the next quarter."
            )
            return AIMessage(content=content)

        # 4. Critic Agent prompt check
        if "critic agent" in prompt_lower or "evaluate" in prompt_lower or "critic_score" in prompt_lower:
            # Return JSON structure that can be parsed
            response_data = {
                "critic_score": 0.85,
                "requires_human": True,  # Pauses for Human review
                "explanation": "The research and analysis are high quality. The pricing strategy aligns with market data. Paused for human approval before executing DB and Slack notifications."
            }
            return AIMessage(content=json.dumps(response_data))

        # 5. Action Agent prompt check
        if "action agent" in prompt_lower or "send_email" in prompt_lower or "slack" in prompt_lower:
            content = (
                "**ACTIONS EXECUTED**:\n"
                "- Simulated database entry: Added competitor intelligence records to table 'competitor_intel'.\n"
                "- Slack webhook notification dispatched: 'Competitor Intelligence alert - Pricing Strategy finalized at $59/month.'\n"
                "- Email alert queued to operations: 'Task Completed: Enterprise AI Triage task executed successfully.'"
            )
            return AIMessage(content=content)

        # Default fallback
        return AIMessage(content="Drafting response: Multi-agent execution step evaluated.")

def get_llm():
    """
    Returns the ChatGoogleGenerativeAI model if configured.
    Otherwise, returns MockLLM.
    """
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key == "your_gemini_api_key_here":
        return MockLLM()
        
    try:
        # Verify package configuration
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
    except Exception as e:
        logger.warning(f"Error initializing ChatGoogleGenerativeAI: {str(e)}. Falling back to MockLLM.")
        return MockLLM()

from langchain_core.messages import AIMessage
from graph.state import AgentState
from graph.tools.search import web_search
from memory.long_term import long_term_mem
from graph.llm import get_llm

def research_node(state: AgentState) -> dict:
    """
    Research Agent Node.
    Uses the LLM to synthesize findings from both external Web Search (Tavily)
    and internal company policies/SLA documents (ChromaDB RAG).
    
    Args:
        state (AgentState): Current graph state.
        
    Returns:
        dict: Updated state dictionary with research_output.
    """
    task = state.get("task", "")
    
    # 1. Query internal vector DB / RAG
    rag_docs = long_term_mem.search(task, n_results=2)
    rag_context = "\n".join([f"- {doc}" for doc in rag_docs]) if rag_docs else "No matching internal documentation found."
    
    # 2. Run external web search
    search_results = web_search(task)
    
    # 3. Request LLM to compile/synthesize a research report
    llm = get_llm()
    prompt = (
        "You are the Research Agent. Your goal is to gather and synthesize findings for the following task.\n"
        f"Task: \"{task}\"\n\n"
        f"--- Internal Company Knowledge Base Docs ---\n{rag_context}\n\n"
        f"--- External Web Search Findings ---\n{search_results}\n\n"
        "Synthesize these findings into a detailed, structured Research Report containing facts, "
        "SLAs, prices, urls, or guidelines. Be clear, concise, and professional."
    )
    
    response = llm.invoke(prompt)
    research_report = response.content
    
    return {
        "research_output": research_report,
        "messages": [AIMessage(content=f"**Research Agent Report**:\n{research_report}", name="ResearchAgent")]
    }

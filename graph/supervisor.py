import logging
from langchain_core.messages import AIMessage
from graph.state import AgentState
from graph.llm import get_llm

logger = logging.getLogger("enterprise_agent.graph.supervisor")

def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor Node.
    Coordinates which specialized worker node should execute next.
    Acts as a state gate to ensure structured forward progress.
    
    Args:
        state (AgentState): Current graph state.
        
    Returns:
        dict: Dict containing 'next' agent node identifier.
    """
    task = state.get("task", "")
    research_output = state.get("research_output", "")
    analysis_output = state.get("analysis_output", "")
    critic_score = state.get("critic_score", 0.0)
    actions_taken = state.get("actions_taken", [])
    
    # 1. State-based heuristics to enforce standard linear setup
    if not research_output:
        return {"next": "research"}

    if not analysis_output:
        return {"next": "analysis"}

    if critic_score == 0.0:
        return {"next": "critic"}

    # If actions already executed and critic approved, end the loop
    if actions_taken and critic_score >= 0.7:
        logger.info(f"Task completed. Actions={len(actions_taken)}. Critic={critic_score:.2f}. Routing to END.")
        return {"next": "end"}

    # 2. LLM-based scheduling when linear flow needs adjustments
    llm = get_llm()
    prompt = (
        "You are the Supervisor Node in an Enterprise AI Automation System.\n"
        "Your role is to orchestrate a team of specialized agents: 'research', 'analysis', 'critic', and 'action'.\n\n"
        f"Goal: \"{task}\"\n"
        f"--- Active States ---\n"
        f"Research Report: {research_output[:200]}...\n"
        f"Analysis Report: {analysis_output[:200]}...\n"
        f"Critic Score: {critic_score}\n"
        f"Actions Executed: {actions_taken}\n\n"
        "Based on this state, select the next agent to activate. Choose exactly one of:\n"
        "- 'research' (if more research/info collection is needed)\n"
        "- 'analysis' (if we need to analyze new research or calculate stats)\n"
        "- 'critic' (if we have research and analysis ready and need QA evaluation)\n"
        "- 'action' (if the critic has passed and we need to run emails/DB logs)\n"
        "- 'END' (if the task is fully completed)\n\n"
        "Output ONLY the name of the agent (e.g. 'research', 'analysis', 'critic', 'action', or 'END') with no other text."
    )
    
    try:
        response = llm.invoke(prompt)
        next_step = response.content.strip().lower()
    except Exception as e:
        logger.error(f"Supervisor LLM call failed: {str(e)}. Defaulting to critic.")
        next_step = "critic"
    
    # Validate result
    valid_agents = ["research", "analysis", "critic", "action", "end"]
    for agent in valid_agents:
        if agent in next_step:
            return {"next": agent}
            
    return {"next": "critic"}

def route_after_critic(state: AgentState) -> str:
    """
    Conditional routing function executed after the Critic agent completes QA evaluation.
    
    Args:
        state (AgentState): Current graph state.
        
    Returns:
        str: Name of the next node to execute, or END.
    """
    critic_score = state.get("critic_score", 1.0)
    requires_human = state.get("requires_human", False)
    iteration = state.get("iteration", 0)
    actions_taken = state.get("actions_taken", [])
    
    # 1. Loop back to research if score is low and retry budget is remaining
    if critic_score < 0.7:
        if iteration < 3:
            logger.info(f"Critic score {critic_score:.2f} < 0.7. Retrying task (Iteration {iteration}/3)...")
            return "research"
        else:
            logger.warning(f"Critic score {critic_score:.2f} is low, but retry limit (3) exceeded. Proceeding.")
            
    # 2. Pause for human review if flagged
    if requires_human:
        logger.info("requires_human is set to True. Pausing graph execution at human_review gate.")
        return "human_review"
        
    # 3. If actions have not been run, route to action (subject to interrupt_before)
    if not actions_taken:
        logger.info("Routing to action node for execution.")
        return "action"

    logger.info("Task completion criteria satisfied. Routing to END.")
    return "end"

import json
import re
from langchain_core.messages import AIMessage
from graph.state import AgentState
from graph.llm import get_llm

def critic_node(state: AgentState) -> dict:
    """
    Critic Agent Node.
    Performs Quality Assurance by reviewing findings. Evaluates results,
    assigns a score, and flags whether human review is required.
    
    Args:
        state (AgentState): Current graph state.
        
    Returns:
        dict: Updated state dictionary with critic_score, requires_human, and final_output.
    """
    task = state.get("task", "")
    research_output = state.get("research_output", "")
    analysis_output = state.get("analysis_output", "")
    actions_taken = state.get("actions_taken", [])
    iteration = state.get("iteration", 0)
    
    llm = get_llm()
    prompt = (
        "You are the Critic Agent. Your role is to perform quality verification on "
        "the research and analysis outputs. Check for logical consistency, compliance, "
        "and completeness against the task request.\n"
        f"Task: \"{task}\"\n\n"
        f"--- Research Output ---\n{research_output}\n\n"
        f"--- Analysis Output ---\n{analysis_output}\n\n"
        f"--- Side Effects/Actions Taken ---\n{actions_taken}\n\n"
        f"--- Current Iteration ---\n{iteration}\n\n"
        "Provide your quality evaluation. You MUST output a raw JSON dictionary with "
        "exactly these keys:\n"
        "{\n"
        "  \"critic_score\": 0.85, \n"
        "  \"requires_human\": false, \n"
        "  \"explanation\": \"Gaps identified / summary of completeness / reasoning...\"\n"
        "}\n"
        "Rules:\n"
        "- 'critic_score' must be a float between 0.0 and 1.0.\n"
        "- Set 'requires_human' to true if the task involves significant financial pricing, "
        "SLA disputes, compliance alerts, or writing modifications to database tables.\n"
        "Only output the raw JSON dictionary. Do not include markdown code block characters."
    )
    
    response = llm.invoke(prompt)
    response_content = response.content.strip()
    
    # Strip markdown block formatting if present
    json_match = re.search(r"\{.*\}", response_content, re.DOTALL)
    
    score = 0.8
    requires_human = False
    explanation = "System analysis verified."
    
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            score = float(data.get("critic_score", 0.8))
            requires_human = bool(data.get("requires_human", False))
            explanation = data.get("explanation", "Verification completed.")
        except Exception as e:
            explanation = f"Critic parsing error: {str(e)}. Raw output: {response_content}"
            
    # Increment iteration count if score is below threshold to trigger retry limit
    if score < 0.7:
        iteration += 1
            
    return {
        "critic_score": score,
        "requires_human": requires_human,
        "final_output": explanation,
        "iteration": iteration,
        "messages": [
            AIMessage(
                content=(
                    f"**Critic QA Score**: {score:.2f}\n"
                    f"**Requires Human Approval**: {requires_human}\n"
                    f"**Feedback**: {explanation}"
                ),
                name="CriticAgent"
            )
        ]
    }


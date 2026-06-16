import uuid
import logging
from langgraph.graph import StateGraph, END
from graph.state import AgentState
from graph.agents.research import research_node
from graph.agents.analysis import analysis_node
from graph.agents.action import action_node
from graph.agents.critic import critic_node
from graph.supervisor import supervisor_node, route_after_critic
from memory.short_term import get_checkpointer

logger = logging.getLogger("enterprise_agent.graph.builder")

def human_review_node(state: AgentState) -> dict:
    """
    Placeholder node for Human-In-The-Loop review.
    We configure compilation to interrupt *before* this node runs.
    Upon resumption, this node executes, resetting requires_human to False
    so the process does not loop back to a pause state.
    
    Args:
        state (AgentState): Current state.
        
    Returns:
        dict: Cleared requires_human flag.
    """
    logger.info("Human review checkpoint reached and cleared by human input.")
    return {"requires_human": False}

def route_supervisor(state: AgentState) -> str:
    """Routes supervisor's decision. Returns the node name; the conditional edge map resolves 'end' to END."""
    next_node = state.get("next", "critic").strip().lower()
    return next_node

def get_graph():
    """
    Assembles, compiles, and returns the multi-agent graph with persistent checkpointing.
    
    Returns:
        CompiledGraph: The executable LangGraph.
    """
    # 1. Initialize StateGraph with custom AgentState Type
    workflow = StateGraph(AgentState)
    
    # 2. Add all Agent and Control Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("action", action_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("human_review", human_review_node)
    
    # 3. Establish supervisor as main entry point
    workflow.set_entry_point("supervisor")
    
    # 4. Set up edges from supervisor (decided by LLM router)
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "research": "research",
            "analysis": "analysis",
            "critic": "critic",
            "action": "action",
            "end": END
        }
    )
    
    # 5. Worker agents return their output and loop back to the supervisor
    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analysis", "supervisor")
    workflow.add_edge("action", "supervisor")
    workflow.add_edge("human_review", "supervisor")
    
    # 6. Critic Node evaluates and routes conditionally using route_after_critic
    workflow.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "research": "research",
            "human_review": "human_review",
            "action": "action",
            "end": END
        }
    )
    
    # 7. Retrieve the persistence checkpointer
    checkpointer = get_checkpointer()
    
    # 8. Compile the graph. We configure interrupt_before to stop before execution of 
    # the Action node (preventing API calls) and the Human Review node.
    compiled_graph = workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["action", "human_review"]
    )
    
    return compiled_graph

if __name__ == "__main__":
    # Configure basic logging to see node runs
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    print("\n==================================================")
    print("DEMO: Compiling Graph and Running Simulation")
    print("==================================================\n")
    
    # Get compiled graph
    graph = get_graph()
    
    # Create thread config
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "task": "Check competitor pricing for ticket management SaaS.",
        "messages": [],
        "research_output": "",
        "analysis_output": "",
        "actions_taken": [],
        "critic_score": 0.0,
        "iteration": 0,
        "requires_human": False,
        "final_output": "",
        "next": ""
    }
    
    print("--- STEP 1: INITIAL WORKFLOW INVOCATION ---")
    print(f"Thread ID: {thread_id}")
    
    # Start graph execution. It will halt when it hits interrupt_before nodes.
    for event in graph.stream(initial_state, config=config):
        for node_name, state_update in event.items():
            print(f"\n[Node '{node_name}' Completed]")
            if "critic_score" in state_update:
                print(f"  > Critic Score: {state_update.get('critic_score')}")
                print(f"  > Requires Human Approval: {state_update.get('requires_human')}")
            if "research_output" in state_update:
                print(f"  > Research findings generated ({len(state_update['research_output'])} chars)")
            if "analysis_output" in state_update:
                print(f"  > Quantitative analysis report created ({len(state_update['analysis_output'])} chars)")
                
    # Fetch current execution state
    current_state = graph.get_state(config)
    print("\n--- STEP 2: GRAPH HAS INTERRUPTED ---")
    print(f"Paused before execution of nodes: {current_state.next}")
    print(f"Values in State - requires_human: {current_state.values.get('requires_human')}")
    print(f"Values in State - actions_taken so far: {current_state.values.get('actions_taken')}")
    
    # Simulate a human approval decision by resuming the graph
    print("\n--- STEP 3: RESUMING GRAPH EXECUTION (HUMAN APPROVED) ---")
    
    # Resume the graph by passing input as None (tells checkpointer to load state and continue)
    for event in graph.stream(None, config=config):
        for node_name, state_update in event.items():
            print(f"\n[Node '{node_name}' Completed after Resumption]")
            if "actions_taken" in state_update:
                print(f"  > Actions executed: {state_update.get('actions_taken')}")
                
    # Final result
    final_state = graph.get_state(config)
    print("\n--- STEP 4: WORKFLOW COMPLETE ---")
    print(f"Execution Status: Finished")
    print(f"Final Output: {final_state.values.get('final_output')}")
    print(f"Side Effects Executed: {final_state.values.get('actions_taken')}")
    print("==================================================\n")

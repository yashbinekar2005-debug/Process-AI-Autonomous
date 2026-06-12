from typing import TypedDict, List, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    State representing the current execution context of the enterprise agent.
    """
    task: str
    messages: Annotated[Sequence[BaseMessage], add_messages]
    research_output: str
    analysis_output: str
    actions_taken: List[str]
    critic_score: float
    iteration: int
    requires_human: bool
    final_output: str
    next: str


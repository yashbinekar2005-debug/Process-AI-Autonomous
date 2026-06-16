import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

from graph.builder import get_graph
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("enterprise_agent.api")

app = FastAPI(
    title="Enterprise AI Automation API",
    description="Backend API for triggering, pausing, and resuming multi-agent enterprise workflows.",
    version="1.0.0"
)

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get reference to the compiled graph
graph = get_graph()

# Request/Response schemas
class TaskCreateRequest(BaseModel):
    task: str

class ResumeRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None

class TaskStatusResponse(BaseModel):
    thread_id: str
    status: str  # "running", "paused", "completed", "error"
    pending_nodes: List[str]
    state: Dict[str, Any]

def serialize_message(m) -> Dict[str, str]:
    """Serializes LangChain message objects into JSON-friendly format."""
    role = "assistant"
    if m.type == "human":
        role = "user"
    elif m.type == "system":
        role = "system"
        
    name = getattr(m, "name", None)
    return {
        "role": role,
        "name": name if name else role.capitalize(),
        "content": str(m.content)
    }

def get_task_status(thread_id: str) -> TaskStatusResponse:
    """Helper to inspect the graph checkpointer and format the task status."""
    config = {"configurable": {"thread_id": thread_id}}
    state_info = graph.get_state(config)
    
    if not state_info.values:
        raise HTTPException(status_code=404, detail=f"Task with thread_id {thread_id} not found.")
        
    values = state_info.values
    pending = list(state_info.next)
    
    # Determine status
    if not pending:
        status = "completed"
    elif any(node in ["action", "human_review"] for node in pending):
        status = "paused"
    else:
        status = "running"
        
    # Serialize state values
    serialized_state = {
        "task": values.get("task", ""),
        "research_output": values.get("research_output", ""),
        "analysis_output": values.get("analysis_output", ""),
        "actions_taken": values.get("actions_taken", []),
        "critic_score": values.get("critic_score", 0.0),
        "iteration": values.get("iteration", 0),
        "requires_human": values.get("requires_human", False),
        "final_output": values.get("final_output", ""),
        "messages": [serialize_message(m) for m in values.get("messages", [])]
    }
    
    return TaskStatusResponse(
        thread_id=thread_id,
        status=status,
        pending_nodes=pending,
        state=serialized_state
    )

@app.post("/api/tasks", response_model=TaskStatusResponse)
async def create_task(payload: TaskCreateRequest):
    """
    Triggers a new business automation process task.
    Creates a new thread and runs the graph until it halts or completes.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "task": payload.task,
        "messages": [HumanMessage(content=payload.task)],
        "research_output": "",
        "analysis_output": "",
        "actions_taken": [],
        "critic_score": 0.0,
        "iteration": 0,
        "requires_human": False,
        "final_output": "",
        "next": ""
    }
    
    logger.info(f"Starting new task on thread {thread_id} for task: {payload.task}")
    
    try:
        # Run graph until pause or completion
        for event in graph.stream(initial_state, config=config):
            pass
        
        return get_task_status(thread_id)
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task start failed: {str(e)}")

@app.get("/api/tasks/{thread_id}", response_model=TaskStatusResponse)
async def get_task(thread_id: str):
    """Retrieves the current execution status and values of an active task thread."""
    return get_task_status(thread_id)

@app.post("/api/tasks/{thread_id}/resume", response_model=TaskStatusResponse)
async def resume_task(thread_id: str, payload: ResumeRequest):
    """
    Resumes a paused graph execution.
    If approved=True, proceeds past approval gates.
    If approved=False, registers feedback and loops back to research.
    """
    config = {"configurable": {"thread_id": thread_id}}
    state_info = graph.get_state(config)
    
    if not state_info.values:
        raise HTTPException(status_code=404, detail="Task thread not found.")
        
    logger.info(f"Human Decision received for thread {thread_id}: Approved={payload.approved}")
    
    try:
        if payload.approved:
            logger.info("Resuming execution...")
            for event in graph.stream(None, config=config):
                pass
            # Keep resuming until graph is no longer paused at interrupt_before nodes
            max_extra = 5
            for _ in range(max_extra):
                state_after = graph.get_state(config)
                if "action" in state_after.next or "human_review" in state_after.next:
                    logger.info(f"Resuming past remaining gate: {state_after.next}")
                    for event in graph.stream(None, config=config):
                        pass
                else:
                    break
        else:
            # Human rejected and provided correction comments
            feedback = payload.feedback if payload.feedback else "Revision requested by human user."
            logger.info(f"Task rejected. Feedback: {feedback}")
            
            # Update the graph state to reset variables, log feedback and trigger loop-back
            graph.update_state(
                config,
                {
                    "messages": [HumanMessage(content=f"Human User Request for Revision: {feedback}")],
                    "critic_score": 0.0,
                    "requires_human": False,
                    "next": "research"  # Loop back to research agent
                }
            )
            
            # Stream the execution after state update
            for event in graph.stream(None, config=config):
                pass
                
        return get_task_status(thread_id)
    except Exception as e:
        logger.error(f"Error resuming task {thread_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Task resumption failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    from config import settings
    logger.info(f"Starting API Server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)

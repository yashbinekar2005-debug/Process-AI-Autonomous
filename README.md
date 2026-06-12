# Walkthrough - Enterprise AI Automation System

We have successfully built the complete codebase for the **Enterprise AI Automation System**. The codebase utilizes a graph-based multi-agent orchestration architecture to handle complex business processes with integrated Redis short-term persistence, vector RAG long-term memory, custom SQLite database operations, and notifications.

---

## Codebase Directory Structure

All files have been written directly to the workspace root:

```plaintext
enterprise-agent/
├── graph/
│   ├── state.py            # AgentState TypedDict with type annotations
│   ├── llm.py              # LLM factory (Gemini / MockLLM fallback)
│   ├── supervisor.py       # Supervisor Orchestration & conditional retry routing
│   ├── builder.py          # Compilation with RedisSaver and HITL pauses
│   ├── agents/
│   │   ├── research.py     # Web search & RAG compiler agent
│   │   ├── analysis.py     # Quantitative analysis & REPL agent
│   │   ├── action.py       # SQL, Slack, and Email side-effects agent
│   │   └── critic.py       # QA score and loop-back trigger agent
│   └── tools/
│       ├── search.py       # Tavily Web Search integration
│       ├── python_repl.py  # Standard output capture Python REPL
│       ├── db_tools.py     # Local SQLite DB queries & ticket creation
│       └── notification.py # Slack webhooks and SMTP email dispatches
├── memory/
│   ├── short_term.py       # RedisSaver checkpointer with MemorySaver fallback
│   └── long_term.py        # ChromaDB setup seeded with default SLAs and policies
├── api/
│   └── main.py             # FastAPI REST endpoints for start/status/resume
├── ui/
│   └── dashboard.py        # Streamlit dashboard interface with premium CSS styling
├── config.py               # Pydantic-settings config mapper
├── requirements.txt        # System requirements
└── .env                    # System-wide configuration variables
```

---

## Architectural Highlights

### 1. State Management & Serialization
- The state uses `add_messages` to compile chat logs from all agents.
- Custom serialization transforms LangChain `BaseMessage` models into JSON representations, allowing the Streamlit UI to dynamically display the conversation bubbles with custom icons (🛡️ for Critic, 🤖 for workers, 👤 for users).

### 2. Multi-Agent Flow Topology
- **Supervisor Hub**: Initiates tasks, manages sequencing (Research ➔ Analysis ➔ Critic QA).
- **Critic Edge**: Inspects results.
  - If `critic_score < 0.7` and `iteration < 3`, it increments the counter and loops back to the `research` node.
  - If `requires_human` is True, it routes to `human_review` which halts execution.
  - Otherwise, it routes to `action` or `END`.
- **Interrupt Gates**: Configured as `interrupt_before=["action", "human_review"]`. When the graph routes to these nodes, it pauses execution and waits for a continuation signal.

### 3. Human-in-the-Loop Resumption & Revision loops
- If approved, the FastAPI endpoint resumes execution by invoking the graph with a `None` state payload.
- If rejected, the human's feedback is written to the state history as a `HumanMessage`, the `critic_score` is reset to `0.0`, and the graph is forced back to the `research` agent to correct the findings.

---

## Run and Verification Instructions

Follow these simple steps in your terminal to start the entire system:

### 1. Set Up Environment
First, create your virtual environment and install the required dependencies:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials
Open the `.env` file in the root folder and add your API keys:
```env
GEMINI_API_KEY=your_real_gemini_key
TAVILY_API_KEY=your_real_tavily_key
```
> [!NOTE]
> If you do not configure `GEMINI_API_KEY` or `TAVILY_API_KEY`, the application will use the pre-built `MockLLM` and mock search engines. This allows you to experience the full cyclic loop, pause gates, and database updates instantly without needing credentials.

### 3. Run FastAPI Backend
Launch the API server to handle graph requests:
```powershell
uvicorn api.main:app --reload --port 8000
```
This starts the backend at `http://127.0.0.1:8000`. You can inspect the Swagger docs at `http://127.0.0.1:8000/docs`.

### 4. Run Streamlit UI
In a separate terminal tab, run the frontend dashboard:
```powershell
streamlit run ui/dashboard.py
```
This opens the browser dashboard. You can enter task instructions, watch the agents complete tasks, check the SQLite database updates, and interact with the **Human-in-the-Loop** approval cards.

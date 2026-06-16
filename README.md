# Enterprise AI Automation System

A graph-based multi-agent orchestration system that automates business processes using LLM-powered agents. Supports **local Ollama (Llama 3.2)** or **Gemini API** with automatic fallback.

## Architecture

```plaintext
enterprise-agent/
├── graph/
│   ├── state.py              # AgentState TypedDict
│   ├── llm.py                # LLM factory: Ollama → Gemini → MockLLM (fallback chain)
│   ├── supervisor.py         # Supervisor orchestration & heuristic routing
│   ├── builder.py            # LangGraph compilation with checkpointer & interrupt gates
│   ├── agents/
│   │   ├── research.py       # Web search + RAG synthesis agent
│   │   ├── analysis.py       # Quantitative analysis + Python REPL agent
│   │   ├── action.py         # SQLite, Slack, Email side-effect agent
│   │   └── critic.py         # QA scoring, retry loop, human-review trigger
│   └── tools/
│       ├── search.py         # Web search: Tavily → DuckDuckGo (free fallback)
│       ├── python_repl.py    # Safe Python REPL with output capture
│       ├── db_tools.py       # Local SQLite queries
│       └── notification.py   # Slack webhook + SMTP email dispatches
├── memory/
│   ├── short_term.py         # RedisSaver checkpointer (falls back to MemorySaver)
│   └── long_term.py          # ChromaDB vector store with SLA/policy seed data
├── api/
│   └── main.py               # FastAPI: create task, get status, resume (with multi-gate handling)
├── ui/
│   └── dashboard.py          # Streamlit dashboard with charts, KPI cards, auto-refresh
├── config.py                 # Pydantic-settings (Ollama, Gemini, retry, etc.)
├── .env.example              # Template for configuration
└── requirements.txt
```

## Agent Workflow

```
User Task → Supervisor → Research → Supervisor → Analysis → Supervisor → Critic
                                                                          │
                              ┌───────────────────────────────────────────┤
                              ▼                                           │
                        Action (DB/Slack/Email)                   score < 0.7?
                              │                                     retry → Research
                              ▼                                     score ≥ 0.7
                         Supervisor ──→ END                     requires_human?
                                                                      │
                                                                      ▼
                                                              Human Review Gate
                                                              (Approve / Revise)
```

## Quick Start

### 1. Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) (optional — skip if using Gemini)

```powershell
ollama pull llama3.2
```

### 2. Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

Copy `.env.example` to `.env` and adjust:

```env
# LLM Provider: "ollama" (default) or "gemini"
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Gemini (fallback if Ollama is unavailable)
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

> No API keys required if using Ollama + DuckDuckGo. Everything runs locally and free.

### 4. Run

**Terminal 1 — API Server:**
```powershell
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 — Dashboard:**
```powershell
streamlit run ui/dashboard.py
```

Open `http://localhost:8501` to use the dashboard.

## LLM Fallback Chain

The system tries providers in order until one succeeds:

| Priority | Provider | Requires |
|----------|----------|----------|
| 1 | Ollama (local) | Ollama running + model pulled |
| 2 | Gemini API | `GEMINI_API_KEY` set |
| 3 | MockLLM | Nothing (canned responses for demo) |

Each provider uses **exponential backoff retry** (configurable via `LLM_MAX_RETRIES` / `LLM_RETRY_DELAY`).

## Web Search Fallback

| Priority | Provider | Requires |
|----------|----------|----------|
| 1 | Tavily API | `TAVILY_API_KEY` set |
| 2 | DuckDuckGo | Nothing (free, no key) |
| 3 | Mock search | Nothing (canned results) |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tasks` | Create and execute a new task |
| `GET` | `/api/tasks/{thread_id}` | Get task status and state |
| `POST` | `/api/tasks/{thread_id}/resume` | Approve/reject a paused task |

## Dashboard Features

- **KPI Cards** — critic score, iteration count, human-review status, actions count
- **Chart Extraction** — auto-detects pricing (`$XX/month`) and percentages (`XX%`) from LLM output → renders bar/pie charts via Plotly
- **Human-in-the-Loop Gate** — approve action execution or request revision with feedback
- **Auto-Refresh** — toggle for live monitoring
- **Dark Glassmorphism Theme** — gradient headers, glow effects, responsive layout

## Example Tasks

```text
"Compare AWS Lambda vs Azure Functions pricing for 1M requests/month"
"Research current salaries for senior engineers in US vs India and compute the difference"
"Find top 3 CRM tools, compare their enterprise pricing, and log results to database"
"Analyze SLA benchmarks for ticket resolution time and send a Slack notification"
```

# Enterprise AI Automation System

An autonomous, multi-agent business process automation platform built with LangGraph. 

This system breaks away from linear chains, utilizing a graph-based architecture to enable cyclic processes, conditional branching, and multi-agent collaboration. It runs complex workflows autonomously—such as competitor analysis, ticket triage, and financial anomaly detection—with human approval gates strategically placed before real-world actions are executed.

## 🚀 Key Features

* **Graph Orchestration:** Powered by LangGraph 1.0 for cyclic workflows and dynamic routing.
* **Multi-Agent Collaboration:** Specialized agents (Research, Analysis, Action, Critic) handle distinct phases of the task.
* **Durable State Persistence:** Uses Redis checkpointer to ensure zero context loss. If the server restarts mid-run, the graph picks up exactly where it left off.
* **Human-in-the-Loop (HITL):** Execution automatically pauses before critical operations (like sending emails or writing to production DBs) awaiting human approval.
* **Self-Correction:** Built-in Critic agent evaluates outputs and triggers retry loops if the quality falls below a defined threshold.

## 🧠 Architecture: The 4 Worker Agents

| Agent | Responsibilities | Tools Used |
| :--- | :--- | :--- |
| **Research Agent** | Gathers context, web search, RAG | Tavily API, ChromaDB, Web Scraper |
| **Analysis Agent** | Data processing, coding, logical deduction | Python REPL, Pandas, SQL |
| **Action Agent** | Executes real-world operations | Email API, Slack API, REST, DB Writes |
| **Critic Agent** | Quality assurance, hallucination checks | LLM-as-judge, Custom Rubrics |

## 🛠 Tech Stack

* **Orchestration:** LangGraph 1.0, LangChain 1.0
* **LLM:** Gemini 1.5 Flash (or GPT-4o)
* **Memory:** ChromaDB / Qdrant (Long-term RAG), Redis (Short-term State)
* **Backend & API:** FastAPI
* **Dashboard UI:** Streamlit
* **Database:** PostgreSQL

## 📂 Codebase Structure

```text
enterprise-agent/
├── graph/
│   ├── state.py              # TypedDict — the shared brain
│   ├── supervisor.py         # Routes tasks to agents
│   ├── agents/               # Logic for specific worker nodes
│   ├── tools/                # External APIs and sandboxes
│   └── builder.py            # Graph compilation and checkpointing
├── memory/                   # Vector stores and Redis checkpointer
├── api/                      # FastAPI endpoints
├── ui/                       # Streamlit dashboard
├── config.py                 # Environment variables
└── requirements.txt
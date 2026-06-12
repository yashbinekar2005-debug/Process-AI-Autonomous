import streamlit as st
import httpx
import json
import time

# Set Page Config for Wide Mode and Dark/Sleek defaults
st.set_page_config(
    page_title="Enterprise AI Orchestrator Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoint URL
API_URL = "http://localhost:8000/api/tasks"

# 1. Custom CSS for Premium Design Aesthetics
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');

/* Main fonts */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #f1f5f9;
}

/* Gradient Titles */
.gradient-header {
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 50%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 2.8rem;
    margin-bottom: 5px;
}

.gradient-subheader {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    color: #cbd5e1;
    margin-top: 0;
    margin-bottom: 25px;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
}

.approval-card {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
}

/* Status Badges */
.status-badge-running {
    background-color: rgba(59, 130, 246, 0.12);
    border: 1px solid #3b82f6;
    color: #60a5fa;
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    text-align: center;
}

.status-badge-paused {
    background-color: rgba(245, 158, 11, 0.12);
    border: 1px solid #f59e0b;
    color: #fbbf24;
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    text-align: center;
}

.status-badge-completed {
    background-color: rgba(16, 185, 129, 0.12);
    border: 1px solid #10b981;
    color: #34d399;
    border-radius: 999px;
    padding: 5px 14px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
    text-align: center;
}

/* Agent Bubble Layouts */
.agent-bubble {
    background-color: rgba(15, 23, 42, 0.6);
    border-left: 4px solid #6366f1;
    padding: 12px 18px;
    margin-bottom: 15px;
    border-radius: 0 10px 10px 0;
}

.critic-bubble {
    background-color: rgba(245, 158, 11, 0.05);
    border-left: 4px solid #f59e0b;
    padding: 12px 18px;
    margin-bottom: 15px;
    border-radius: 0 10px 10px 0;
}

.user-bubble {
    background-color: rgba(51, 65, 85, 0.4);
    border-left: 4px solid #94a3b8;
    padding: 12px 18px;
    margin-bottom: 15px;
    border-radius: 0 10px 10px 0;
}

.agent-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: #cbd5e1;
    margin-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# 2. State management
if "threads" not in st.session_state:
    st.session_state["threads"] = []
if "current_thread" not in st.session_state:
    st.session_state["current_thread"] = None

# Header Title UI
st.markdown('<div class="gradient-header">Enterprise AI Orchestrator</div>', unsafe_allow_html=True)
st.markdown('<div class="gradient-subheader">Multi-Agent Business Process Automation Hub</div>', unsafe_allow_html=True)

# 3. Sidebar Configuration
st.sidebar.markdown("### ⚙️ System Configuration")

# Test Connection Status
api_status = False
try:
    # Just check if backend endpoint answers
    response = httpx.get(API_URL.replace("/tasks", ""))
    api_status = True
except Exception:
    api_status = False

if api_status:
    st.sidebar.success("● API Backend: Connected")
else:
    st.sidebar.error("○ API Backend: Disconnected")
    st.sidebar.markdown(
        "> [!WARNING]\n"
        "> The API backend is not detected. Please run the server in your terminal:\n"
        "> `uvicorn api.main:app --reload --port 8000`"
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Trigger New Task")
new_task_input = st.sidebar.text_area(
    "Describe the Business Process:",
    placeholder="e.g. Compare SaaS support plans from Zendesk vs Salesforce. Calculate savings and update tickets.",
    height=120
)

if st.sidebar.button("Trigger Automation Process", use_container_width=True):
    if not new_task_input.strip():
        st.sidebar.warning("Please enter a task description first.")
    elif not api_status:
        st.sidebar.error("Cannot connect to API server. Please start the backend.")
    else:
        with st.spinner("Initializing multi-agent graph..."):
            try:
                res = httpx.post(API_URL, json={"task": new_task_input}, timeout=60.0)
                if res.status_code == 200:
                    task_data = res.json()
                    tid = task_data["thread_id"]
                    if tid not in st.session_state["threads"]:
                        st.session_state["threads"].insert(0, tid)
                    st.session_state["current_thread"] = tid
                    st.toast("Automation initiated successfully!")
                else:
                    st.sidebar.error(f"Error starting task: {res.text}")
            except Exception as e:
                st.sidebar.error(f"API Connection error: {str(e)}")

# Select thread history dropdown
st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Execution Threads")

if st.session_state["threads"]:
    selected_thread = st.sidebar.selectbox(
        "Active Task Threads:",
        st.session_state["threads"],
        index=0 if st.session_state["current_thread"] not in st.session_state["threads"] else st.session_state["threads"].index(st.session_state["current_thread"])
    )
    if selected_thread != st.session_state["current_thread"]:
        st.session_state["current_thread"] = selected_thread
else:
    st.sidebar.info("No active execution threads. Enter a process to begin.")
    selected_thread = None

# Refresh button
if selected_thread and st.sidebar.button("Refresh Thread State", use_container_width=True):
    st.rerun()

# 4. Main Panel Logic
if not selected_thread:
    # Showcase information card if empty
    st.markdown("""
    <div class="glass-card">
        <h3>Welcome to the Enterprise AI Automation System</h3>
        <p>This orchestrator uses a graph-based cyclic flow to execute enterprise business workflows autonomously.</p>
        <p>The orchestrator coordinates four specialized agents:</p>
        <ul>
            <li><strong>Research Agent:</strong> Web search and semantic knowledge retrieval.</li>
            <li><strong>Analysis Agent:</strong> Numerical computations and Python code REPL analysis.</li>
            <li><strong>Critic Agent:</strong> QA auditing, hallucinations detection, scoring, and retry coordination.</li>
            <li><strong>Action Agent:</strong> Writing back to SQLite DB, triggering SMTP emails, and Slack Webhooks (requires human approval).</li>
        </ul>
        <p><em>To get started, describe a task in the left panel and click <strong>Trigger Automation Process</strong>.</em></p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Query API for state
    try:
        res = httpx.get(f"{API_URL}/{selected_thread}")
        if res.status_code == 200:
            task_status = res.json()
            state_vals = task_status["state"]
            status_label = task_status["status"]
            pending = task_status["pending_nodes"]
            
            # Display summary header card
            col_info, col_stat = st.columns([3, 1])
            with col_info:
                st.markdown(f"#### Thread ID: `{selected_thread}`")
                st.markdown(f"**Task**: {state_vals.get('task')}")
            with col_stat:
                # Format status badge
                if status_label == "completed":
                    st.markdown('<div class="status-badge-completed">🟢 Completed</div>', unsafe_allow_html=True)
                elif status_label == "paused":
                    st.markdown('<div class="status-badge-paused">🟡 Paused (Awaiting Human)</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-badge-running">🔵 Running / Processing</div>', unsafe_allow_html=True)
                    
            # 5. Human-in-the-Loop Review Gate
            if status_label == "paused":
                st.markdown('<div class="approval-card">', unsafe_allow_html=True)
                st.markdown("### ⚠️ Human-in-the-Loop Approval Required")
                st.write(f"The process is currently paused before executing: **`{pending}`**.")
                st.write("Review the agent outputs below. You can approve and trigger operations, or request changes and force agents to revise.")
                
                # Feedback text area
                feedback_txt = st.text_area("Revision Feedback (Only needed if rejecting):", placeholder="e.g. Please search for Gamma Co as well, and recalculate the pricing structure.")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("👍 Approve Execution & Complete", use_container_width=True):
                        with st.spinner("Resuming workflow..."):
                            res_resume = httpx.post(f"{API_URL}/{selected_thread}/resume", json={"approved": True})
                            if res_resume.status_code == 200:
                                st.success("Task approved and executed!")
                                time.sleep(1.0)
                                st.rerun()
                            else:
                                st.error("Failed to resume task.")
                with col_btn2:
                    if st.button("👎 Request Revision & Loop Back", use_container_width=True):
                        if not feedback_txt.strip():
                            st.warning("Please provide revision feedback description.")
                        else:
                            with st.spinner("Routing back to Research agent..."):
                                res_resume = httpx.post(f"{API_URL}/{selected_thread}/resume", json={"approved": False, "feedback": feedback_txt})
                                if res_resume.status_code == 200:
                                    st.info("Feedback registered. Retrying graph steps...")
                                    time.sleep(1.0)
                                    st.rerun()
                                else:
                                    st.error("Failed to route back.")
                st.markdown('</div>', unsafe_allow_html=True)

            # 6. Tabbed Output Panels
            tab_logs, tab_research, tab_analysis, tab_actions = st.tabs([
                "💬 Agent Message Logs", 
                "🔍 Research Report", 
                "📊 Code & Analysis", 
                "⚡ Side Effects Executed"
            ])
            
            with tab_logs:
                st.markdown("### Multi-Agent Conversational History")
                for msg in state_vals.get("messages", []):
                    role = msg["role"]
                    name = msg["name"]
                    content = msg["content"]
                    
                    if "CriticAgent" in name:
                        bubble_style = "critic-bubble"
                        icon = "🛡️"
                    elif "user" in role:
                        bubble_style = "user-bubble"
                        icon = "👤"
                    else:
                        bubble_style = "agent-bubble"
                        icon = "🤖"
                        
                    st.markdown(f"""
                    <div class="{bubble_style}">
                        <div class="agent-title">{icon} {name}</div>
                        <div>{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with tab_research:
                st.markdown("### Research Findings Output")
                research_text = state_vals.get("research_output")
                if research_text:
                    st.markdown(research_text)
                else:
                    st.info("No research report generated yet.")
                    
            with tab_analysis:
                st.markdown("### Analytical Computations & Reasoning")
                analysis_text = state_vals.get("analysis_output")
                if analysis_text:
                    st.markdown(analysis_text)
                else:
                    st.info("No analysis output generated yet.")
                    
            with tab_actions:
                st.markdown("### DB Updates, Slack Notifications & Emails")
                actions = state_vals.get("actions_taken", [])
                if actions:
                    for a in actions:
                        st.markdown(f"- {a}")
                else:
                    st.info("No external actions have been executed yet (awaits human approval).")
                    
            # Iteration tracker footer
            st.markdown("---")
            st.markdown(
                f"**System Statistics**: "
                f"Critic Rating Score: `{state_vals.get('critic_score')}` | "
                f"Retry Loops: `{state_vals.get('iteration')}/3` | "
                f"Human approval flag: `{state_vals.get('requires_human')}`"
            )
            
        else:
            st.error(f"Failed to fetch task details. Status code: {res.status_code}")
    except Exception as e:
        st.error(f"Failed to load task state from FastAPI: {str(e)}")

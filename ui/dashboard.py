import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import uuid
import time
import re
import plotly.express as px
import pandas as pd
from langchain_core.messages import HumanMessage

st.set_page_config(
    page_title="Enterprise AI Orchestrator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}
.stApp {
    background: #0a0f1e;
    background: linear-gradient(135deg, #0a0f1e 0%, #0f1729 50%, #0a0f1e 100%);
}

.gradient-header {
    background: linear-gradient(135deg, #a78bfa 0%, #818cf8 40%, #6366f1 70%, #4f46e5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Outfit', sans-serif;
    font-weight: 800;
    font-size: 2.6rem;
    line-height: 1.2;
}
.gradient-subheader {
    font-family: 'Outfit', sans-serif;
    font-weight: 400;
    color: #64748b;
    font-size: 0.95rem;
    letter-spacing: 0.3px;
}

.glass-card {
    background: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    transition: border-color 0.3s;
}
.glass-card:hover {
    border-color: rgba(129, 140, 248, 0.15);
}

.kpi-card {
    background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.kpi-value {
    font-family: 'Outfit', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #f1f5f9;
}
.kpi-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 2px;
}

.approval-card {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.06), rgba(245, 158, 11, 0.02));
    border: 1px solid rgba(245, 158, 11, 0.2);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    font-family: 'Outfit', sans-serif;
}
.status-completed { background: rgba(16, 185, 129, 0.1); border: 1px solid #10b981; color: #34d399; }
.status-paused { background: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; color: #fbbf24; }
.status-running { background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; color: #60a5fa; }

.agent-bubble {
    background: rgba(15, 23, 42, 0.5);
    border-left: 3px solid #6366f1;
    padding: 12px 18px;
    margin-bottom: 12px;
    border-radius: 0 10px 10px 0;
}
.critic-bubble {
    background: rgba(245, 158, 11, 0.04);
    border-left: 3px solid #f59e0b;
    padding: 12px 18px;
    margin-bottom: 12px;
    border-radius: 0 10px 10px 0;
}
.user-bubble {
    background: rgba(51, 65, 85, 0.2);
    border-left: 3px solid #475569;
    padding: 12px 18px;
    margin-bottom: 12px;
    border-radius: 0 10px 10px 0;
}
.agent-title {
    font-weight: 600;
    font-size: 0.85rem;
    color: #94a3b8;
    margin-bottom: 4px;
}

.section-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    color: #cbd5e1;
    margin-bottom: 12px;
}

div[data-testid="stTabs"] button {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "threads" not in st.session_state:
    st.session_state["threads"] = {}
if "current_thread" not in st.session_state:
    st.session_state["current_thread"] = None
if "auto_refresh" not in st.session_state:
    st.session_state["auto_refresh"] = False
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "llm_provider" not in st.session_state:
    st.session_state["llm_provider"] = "gemini"

# --- Helpers ---
def serialize_message(m):
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

def extract_chart_data(text):
    if not text:
        return {}
    data = {}

    pricing_pattern = r'([A-Za-z][A-Za-z\s]+?)\s*[:\-]?\s*\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:/\s*(?:month|mo|yr|year|user|seat|agent))'
    pricing_matches = re.findall(pricing_pattern, text, re.IGNORECASE)
    if pricing_matches:
        items = []
        for name, price in pricing_matches:
            clean_name = name.strip().rstrip(',').rstrip(':')
            clean_price = float(price.replace(',', ''))
            items.append((clean_name, clean_price))
        if items:
            data["bar"] = {"type": "pricing", "items": items, "title": "Pricing Comparison ($/month)"}

    percent_pattern = r'([A-Za-z][A-Za-z\s]+?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*%'
    percent_matches = re.findall(percent_pattern, text, re.IGNORECASE)
    if percent_matches:
        items = []
        for label, val in percent_matches:
            clean_label = label.strip().rstrip(',').rstrip(':')
            items.append((clean_label, float(val)))
        if items:
            data["pie"] = {"items": items, "title": "Distribution Breakdown"}

    if "bar" not in data:
        list_pattern = r'(?:^|\n)\s*[\-\*]\s*(.+?)\s*[:\-]?\s*\$(\d+(?:,\d{3})*(?:\.\d+)?)'
        list_matches = re.findall(list_pattern, text, re.IGNORECASE | re.MULTILINE)
        if list_matches:
            items = [(name.strip(), float(price.replace(',', ''))) for name, price in list_matches[:10]]
            if items:
                data["bar"] = {"type": "generic", "items": items, "title": "Extracted Metrics ($)"}

    return data

def render_charts(chart_data):
    if not chart_data:
        st.info("No structured data available for visualization. The agent's output is text-based.")
        return

    col1, col2 = st.columns(2)

    if "pie" in chart_data:
        with col1:
            items = chart_data["pie"]["items"]
            df = pd.DataFrame(items, columns=["Category", "Value"])
            fig = px.pie(df, values="Value", names="Category",
                         title=chart_data["pie"]["title"],
                         color_discrete_sequence=px.colors.sequential.Viridis,
                         hole=0.4)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1", title_font_color="#f1f5f9",
                margin=dict(t=40, b=20, l=20, r=20)
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

    if "bar" in chart_data:
        with col2 if "pie" in chart_data else col1:
            items = chart_data["bar"]["items"]
            df = pd.DataFrame(items, columns=["Entity", "Value"])
            fig = px.bar(df, x="Entity", y="Value",
                         title=chart_data["bar"]["title"],
                         color="Value", color_continuous_scale="viridis",
                         text_auto='.2s')
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font_color="#cbd5e1", title_font_color="#f1f5f9",
                xaxis_title=None, yaxis_title="Price ($)",
                margin=dict(t=40, b=20, l=20, r=20)
            )
            fig.update_traces(textfont_color="#f1f5f9")
            st.plotly_chart(fig, use_container_width=True)

def render_kpi_metrics(state_vals):
    cols = st.columns(5)
    metrics = [
        ("Critic Score", f"{state_vals.get('critic_score', 0.0):.2f}", "score"),
        ("Iteration", f"{state_vals.get('iteration', 0)}/3", "loop"),
        ("Human Review", "Required" if state_vals.get("requires_human") else "Auto", "flag"),
        ("Actions", f"{len(state_vals.get('actions_taken', []))}", "actions"),
        ("Threads", f"{len(st.session_state['threads'])}", "threads"),
    ]
    colors = ["#818cf8", "#34d399", "#f59e0b", "#f472b6", "#60a5fa"]
    for i, (label, value, _) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="color:{colors[i]}">{value}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">'
                '<span style="font-size:1.6rem;">⚡</span>'
                '<span style="font-family:Outfit;font-weight:700;font-size:1.3rem;color:#e2e8f0;">Enterprise AI</span>'
                '</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#475569;font-size:0.8rem;margin-top:-8px;margin-bottom:20px;">Multi-Agent Automation Hub</p>', unsafe_allow_html=True)

    # --- API Key & Provider Settings ---
    st.markdown('<p style="font-family:Outfit;font-weight:600;font-size:0.9rem;color:#cbd5e1;">🔑 Settings</p>', unsafe_allow_html=True)

    llm_provider = st.selectbox(
        "LLM Provider",
        ["gemini", "ollama"],
        index=0 if st.session_state["llm_provider"] == "gemini" else 1,
        label_visibility="collapsed"
    )

    if llm_provider == "gemini":
        api_key = st.text_input(
            "Gemini API Key",
            value=st.session_state["api_key"],
            type="password",
            placeholder="Enter your Gemini API key...",
            label_visibility="collapsed"
        )
        if api_key != st.session_state["api_key"]:
            st.session_state["api_key"] = api_key
            st.cache_resource.clear()
            st.rerun()
    else:
        ollama_url = st.text_input(
            "Ollama URL",
            value="http://localhost:11434",
            placeholder="http://localhost:11434",
            label_visibility="collapsed"
        )

    if llm_provider != st.session_state["llm_provider"]:
        st.session_state["llm_provider"] = llm_provider
        st.cache_resource.clear()
        st.rerun()

    # Show connection status
    has_key = bool(st.session_state["api_key"]) if llm_provider == "gemini" else True
    if has_key:
        st.markdown('<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.15);border-radius:8px;margin:12px 0 16px;"><span style="color:#34d399;font-size:0.7rem;">●</span><span style="color:#94a3b8;font-size:0.8rem;">Graph Ready (Direct Mode)</span></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);border-radius:8px;margin:12px 0 16px;"><span style="color:#ef4444;font-size:0.7rem;">●</span><span style="color:#94a3b8;font-size:0.8rem;">No API Key Provided</span></div>', unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.04);margin:16px 0;"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-family:Outfit;font-weight:600;font-size:0.9rem;color:#cbd5e1;">🚀 New Task</p>', unsafe_allow_html=True)
    new_task = st.text_area(
        "Task Description",
        placeholder="e.g. Compare AWS vs Azure pricing for 1M requests. Calculate savings.",
        height=100, label_visibility="collapsed"
    )

    trigger_col, refresh_col = st.columns([3, 1])
    with trigger_col:
        triggered = st.button("Trigger Automation", use_container_width=True, type="primary")
    with refresh_col:
        if st.button("↻", use_container_width=True, help="Refresh current thread"):
            st.rerun()

    if triggered:
        if not new_task.strip():
            st.warning("Enter a task first.")
        elif not has_key:
            st.error("Enter your API key first.")
        else:
            st.rerun()

    st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.04);margin:16px 0;"></div>', unsafe_allow_html=True)
    st.markdown('<p style="font-family:Outfit;font-weight:600;font-size:0.9rem;color:#cbd5e1;">📂 Threads</p>', unsafe_allow_html=True)

    auto_refresh = st.toggle("Auto-refresh (5s)", value=st.session_state["auto_refresh"])
    if auto_refresh != st.session_state["auto_refresh"]:
        st.session_state["auto_refresh"] = auto_refresh
        st.rerun()

    if st.session_state["threads"]:
        thread_ids = list(st.session_state["threads"].keys())
        labels = [f"{tid[:8]}... — {st.session_state['threads'][tid].get('task', '')[:40]}" for tid in thread_ids]
        current_idx = 0
        if st.session_state["current_thread"] in thread_ids:
            current_idx = thread_ids.index(st.session_state["current_thread"])

        selected_label = st.selectbox(
            "Select thread:",
            labels,
            index=current_idx,
            label_visibility="collapsed"
        )
        selected_idx = labels.index(selected_label)
        selected_tid = thread_ids[selected_idx]
        if selected_tid != st.session_state["current_thread"]:
            st.session_state["current_thread"] = selected_tid
            st.rerun()

        if st.button("Clear All Threads", use_container_width=True):
            st.session_state["threads"] = {}
            st.session_state["current_thread"] = None
            st.rerun()
    else:
        st.markdown('<p style="color:#475569;font-size:0.85rem;text-align:center;padding:12px 0;">No threads yet.<br>Trigger a task to begin.</p>', unsafe_allow_html=True)

# --- Load Graph (after sidebar so API key is available) ---
@st.cache_resource
def load_graph(api_key, provider):
    from config import settings
    if api_key:
        settings.GEMINI_API_KEY = api_key
    if provider:
        settings.LLM_PROVIDER = provider
    from graph.builder import get_graph
    return get_graph()

graph = load_graph(st.session_state["api_key"], st.session_state["llm_provider"])

def get_task_status(thread_id):
    config = {"configurable": {"thread_id": thread_id}}
    state_info = graph.get_state(config)

    if not state_info.values:
        return None

    values = state_info.values
    pending = list(state_info.next)

    if not pending:
        status = "completed"
    elif any(node in ["action", "human_review"] for node in pending):
        status = "paused"
    else:
        status = "running"

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

    return {
        "thread_id": thread_id,
        "status": status,
        "pending_nodes": pending,
        "state": serialized_state
    }

# --- Handle Task Trigger ---
if triggered and new_task.strip() and has_key:
    with st.spinner("Running multi-agent graph..."):
        try:
            thread_id = str(uuid.uuid4())
            config = {"configurable": {"thread_id": thread_id}}

            initial_state = {
                "task": new_task,
                "messages": [HumanMessage(content=new_task)],
                "research_output": "",
                "analysis_output": "",
                "actions_taken": [],
                "critic_score": 0.0,
                "iteration": 0,
                "requires_human": False,
                "final_output": "",
                "next": ""
            }

            for event in graph.stream(initial_state, config=config):
                pass

            st.session_state["threads"][thread_id] = {
                "task": new_task,
                "created_at": time.time()
            }
            st.session_state["current_thread"] = thread_id
            st.success("Task started!")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- Main Panel ---
st.markdown('<div class="gradient-header">Enterprise AI Orchestrator</div>', unsafe_allow_html=True)
st.markdown('<div class="gradient-subheader">Multi-Agent Business Process Automation Hub</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if not st.session_state["current_thread"]:
    st.markdown("""
    <div class="glass-card" style="text-align:center;padding:48px 24px;">
        <div style="font-size:3rem;margin-bottom:16px;">⚡</div>
        <h3 style="font-family:Outfit;font-weight:600;color:#cbd5e1;margin-bottom:8px;">Welcome to Enterprise AI Orchestrator</h3>
        <p style="color:#64748b;max-width:600px;margin:0 auto;line-height:1.6;">
            A multi-agent automation system powered by LangGraph.<br>
            Describe a business task → the agents research, analyze, critique, and act autonomously.
        </p>
        <div style="display:flex;justify-content:center;gap:24px;margin-top:24px;flex-wrap:wrap;">
            <div style="text-align:center;padding:12px 20px;background:rgba(99,102,241,0.06);border-radius:10px;border:1px solid rgba(99,102,241,0.1);min-width:120px;">
                <div style="font-size:1.4rem;font-weight:700;color:#818cf8;">🔍</div>
                <div style="font-size:0.75rem;color:#64748b;">Research</div>
            </div>
            <div style="text-align:center;padding:12px 20px;background:rgba(52,211,153,0.06);border-radius:10px;border:1px solid rgba(52,211,153,0.1);min-width:120px;">
                <div style="font-size:1.4rem;font-weight:700;color:#34d399;">📊</div>
                <div style="font-size:0.75rem;color:#64748b;">Analysis</div>
            </div>
            <div style="text-align:center;padding:12px 20px;background:rgba(245,158,11,0.06);border-radius:10px;border:1px solid rgba(245,158,11,0.1);min-width:120px;">
                <div style="font-size:1.4rem;font-weight:700;color:#f59e0b;">🛡️</div>
                <div style="font-size:0.75rem;color:#64748b;">Critic QA</div>
            </div>
            <div style="text-align:center;padding:12px 20px;background:rgba(244,114,182,0.06);border-radius:10px;border:1px solid rgba(244,114,182,0.1);min-width:120px;">
                <div style="font-size:1.4rem;font-weight:700;color:#f472b6;">⚡</div>
                <div style="font-size:0.75rem;color:#64748b;">Action</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    if st.session_state["auto_refresh"]:
        time.sleep(0.1)
        st.rerun()

    task_data = get_task_status(st.session_state["current_thread"])

    if not task_data:
        st.error("Failed to fetch task state. Thread may have expired.")
    else:
        state = task_data["state"]
        status = task_data["status"]
        pending = task_data["pending_nodes"]

        render_kpi_metrics(state)

        st.markdown("<br>", unsafe_allow_html=True)
        info_col, badge_col = st.columns([4, 1])
        with info_col:
            st.markdown(f'<span style="font-family:Outfit;font-weight:600;color:#94a3b8;font-size:0.8rem;">THREAD</span> <code style="background:#1e293b;padding:2px 8px;border-radius:6px;font-size:0.8rem;">{st.session_state["current_thread"][:8]}...</code>', unsafe_allow_html=True)
            st.markdown(f'<p style="color:#e2e8f0;margin-top:4px;font-size:0.95rem;">{state.get("task", "")}</p>', unsafe_allow_html=True)
        with badge_col:
            cls = {"completed": "status-completed", "paused": "status-paused", "running": "status-running"}.get(status, "status-running")
            icon = {"completed": "🟢", "paused": "🟡", "running": "🔵"}.get(status, "🔵")
            label = {"completed": "Completed", "paused": "Paused", "running": "Running"}.get(status, "Running")
            st.markdown(f'<div class="status-badge {cls}">{icon} {label}</div>', unsafe_allow_html=True)

        if status == "paused":
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="approval-card">', unsafe_allow_html=True)
            st.markdown(f'<p style="font-family:Outfit;font-weight:600;color:#fbbf24;font-size:1rem;">⚠️ Human Approval Required</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color:#94a3b8;font-size:0.85rem;">Paused before: <code style="background:#1e293b;padding:2px 6px;border-radius:4px;">{pending}</code></p>', unsafe_allow_html=True)

            feedback = st.text_area("Revision feedback (only if rejecting):", placeholder="e.g. Search for Gamma Co too...", height=80)
            a1, a2 = st.columns(2)
            with a1:
                if st.button("✅ Approve & Execute", use_container_width=True):
                    try:
                        tid = st.session_state["current_thread"]
                        config = {"configurable": {"thread_id": tid}}
                        state_info = graph.get_state(config)

                        if state_info.values:
                            for event in graph.stream(None, config=config):
                                pass

                            max_extra = 5
                            for _ in range(max_extra):
                                state_after = graph.get_state(config)
                                if "action" in state_after.next or "human_review" in state_after.next:
                                    for event in graph.stream(None, config=config):
                                        pass
                                else:
                                    break

                            st.success("Approved! Resuming...")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            with a2:
                if st.button("🔄 Request Revision", use_container_width=True):
                    if not feedback.strip():
                        st.warning("Provide feedback first.")
                    else:
                        try:
                            tid = st.session_state["current_thread"]
                            config = {"configurable": {"thread_id": tid}}

                            graph.update_state(
                                config,
                                {
                                    "messages": [HumanMessage(content=f"Human User Request for Revision: {feedback}")],
                                    "critic_score": 0.0,
                                    "requires_human": False,
                                    "next": "research"
                                }
                            )

                            for event in graph.stream(None, config=config):
                                pass

                            st.info("Feedback sent. Looping back to research...")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        tabs = st.tabs(["📊 Dashboard", "💬 Messages", "🔍 Research", "📈 Analysis", "⚡ Actions"])

        with tabs[0]:
            research_text = state.get("research_output", "")
            analysis_text = state.get("analysis_output", "")

            chart_data = extract_chart_data(research_text + "\n" + analysis_text)

            if chart_data:
                st.markdown('<p class="section-title">📊 Visual Insights</p>', unsafe_allow_html=True)
                render_charts(chart_data)
            else:
                st.markdown('<p class="section-title">📊 Visual Insights</p>', unsafe_allow_html=True)
                st.info("No structured numerical data detected for charts. The agent output is text-based. Try a comparison task like 'Compare AWS vs Azure pricing'.")

            st.markdown("<br>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<p class="section-title">🔍 Research Summary</p>', unsafe_allow_html=True)
                if research_text:
                    st.markdown(f'<div style="background:rgba(15,23,42,0.3);border-radius:10px;padding:16px;max-height:300px;overflow-y:auto;font-size:0.85rem;color:#cbd5e1;line-height:1.6;">{research_text[:2000]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color:#475569;">Pending...</p>', unsafe_allow_html=True)
            with col2:
                st.markdown('<p class="section-title">📈 Analysis Summary</p>', unsafe_allow_html=True)
                if analysis_text:
                    st.markdown(f'<div style="background:rgba(15,23,42,0.3);border-radius:10px;padding:16px;max-height:300px;overflow-y:auto;font-size:0.85rem;color:#cbd5e1;line-height:1.6;">{analysis_text[:2000]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color:#475569;">Pending...</p>', unsafe_allow_html=True)

        with tabs[1]:
            st.markdown('<p class="section-title">💬 Agent Conversation Log</p>', unsafe_allow_html=True)
            for msg in state.get("messages", []):
                role = msg["role"]
                name = msg["name"]
                content = msg["content"]
                if "CriticAgent" in name:
                    cls = "critic-bubble"; icon = "🛡️"
                elif "user" in role:
                    cls = "user-bubble"; icon = "👤"
                else:
                    cls = "agent-bubble"; icon = "🤖"
                st.markdown(f'<div class="{cls}"><div class="agent-title">{icon} {name}</div><div style="font-size:0.85rem;">{content}</div></div>', unsafe_allow_html=True)

        with tabs[2]:
            st.markdown('<p class="section-title">🔍 Full Research Report</p>', unsafe_allow_html=True)
            if research_text:
                st.markdown(f'<div style="background:rgba(15,23,42,0.3);border-radius:10px;padding:20px;font-size:0.85rem;color:#cbd5e1;line-height:1.7;">{research_text}</div>', unsafe_allow_html=True)
            else:
                st.info("No research output yet.")

        with tabs[3]:
            st.markdown('<p class="section-title">📈 Full Analysis Report</p>', unsafe_allow_html=True)
            if analysis_text:
                st.markdown(f'<div style="background:rgba(15,23,42,0.3);border-radius:10px;padding:20px;font-size:0.85rem;color:#cbd5e1;line-height:1.7;">{analysis_text}</div>', unsafe_allow_html=True)
            else:
                st.info("No analysis output yet.")

        with tabs[4]:
            st.markdown('<p class="section-title">⚡ Side Effects Executed</p>', unsafe_allow_html=True)
            actions = state.get("actions_taken", [])
            if actions:
                for a in actions:
                    st.markdown(f'<div style="background:rgba(16,185,129,0.04);border:1px solid rgba(16,185,129,0.1);border-radius:8px;padding:10px 14px;margin-bottom:8px;font-size:0.85rem;color:#94a3b8;">→ {a}</div>', unsafe_allow_html=True)
            else:
                st.info("No actions executed yet (awaits human approval or task completion).")

        st.markdown('<div style="border-top:1px solid rgba(255,255,255,0.04);margin-top:24px;padding-top:16px;">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="display:flex;gap:24px;font-size:0.8rem;color:#475569;">'
            f'<span>Critic Score: <strong style="color:#818cf8;">{state.get("critic_score", 0.0):.2f}</strong></span>'
            f'<span>Iteration: <strong style="color:#34d399;">{state.get("iteration", 0)}/3</strong></span>'
            f'<span>Human Review: <strong style="color:#f59e0b;">{"⚠️ Required" if state.get("requires_human") else "✅ Auto"}</strong></span>'
            f'<span>Actions: <strong style="color:#f472b6;">{len(actions)}</strong></span>'
            f'</div>', unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

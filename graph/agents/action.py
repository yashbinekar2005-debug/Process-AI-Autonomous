import json
import re
from langchain_core.messages import AIMessage
from graph.state import AgentState
from graph.tools.notification import send_slack_message, send_email
from graph.tools.db_tools import execute_query
from graph.llm import get_llm

def action_node(state: AgentState) -> dict:
    """
    Action Agent Node.
    Decides and triggers external side effects like database operations,
    Slack alerts, and emails. Runs only after human approval.
    
    Args:
        state (AgentState): Current graph state.
        
    Returns:
        dict: Updated state dictionary with actions_taken.
    """
    task = state.get("task", "")
    research_output = state.get("research_output", "")
    analysis_output = state.get("analysis_output", "")
    
    llm = get_llm()
    prompt = (
        "You are the Action Agent. Your job is to select and run business actions based on "
        "the task and agent reports.\n"
        f"Task: \"{task}\"\n\n"
        f"--- Research Output ---\n{research_output}\n\n"
        f"--- Analysis Output ---\n{analysis_output}\n\n"
        "Select valid actions. You can perform SQL queries on a local SQLite DB, send Slack "
        "notifications, or send emails. Output a raw JSON list containing dictionaries with a 'type' key. "
        "Do not wrap the output in markdown block decorations or write introductory text. Follow these schemas:\n"
        "[\n"
        "  {\"type\": \"db\", \"query\": \"INSERT INTO competitor_intel (company, key_finding) VALUES ('Alpha Co', 'Pricing is $49/mo')\"},\n"
        "  {\"type\": \"slack\", \"message\": \"Slack Alert: Competitor intel processed for Alpha Co\"},\n"
        "  {\"type\": \"email\", \"subject\": \"Competitor Intel Report\", \"body\": \"Details about Alpha Co...\"}\n"
        "]\n"
        "If no external side effects are required, return an empty JSON list []."
    )
    
    response = llm.invoke(prompt)
    response_content = response.content.strip()
    
    # Strip markdown block formatting if present
    json_match = re.search(r"\[.*\]", response_content, re.DOTALL)
    actions_executed = []
    
    if json_match:
        try:
            actions_list = json.loads(json_match.group(0))
            for action in actions_list:
                action_type = action.get("type")
                if action_type == "db":
                    query = action.get("query")
                    res = execute_query(query)
                    actions_executed.append(f"DB Write Success: {query} -> Result: {res}")
                elif action_type == "slack":
                    msg = action.get("message")
                    res = send_slack_message(msg)
                    actions_executed.append(f"Slack Notification Sent -> Result: {res}")
                elif action_type == "email":
                    subject = action.get("subject", "Enterprise Alert")
                    body = action.get("body", "")
                    res = send_email(subject, body)
                    actions_executed.append(f"Email Dispatched -> Result: {res}")
        except Exception as e:
            actions_executed.append(f"Error parsing and executing actions: {str(e)}. Raw: {response_content}")
    else:
        # Default fallback: Log what it returned
        actions_executed.append(f"No automated action parsed. Response was: {response_content}")
        
    return {
        "actions_taken": state.get("actions_taken", []) + actions_executed,
        "messages": [AIMessage(content=f"**Action Executed Summary**:\n" + "\n".join([f"- {a}" for a in actions_executed]), name="ActionAgent")]
    }

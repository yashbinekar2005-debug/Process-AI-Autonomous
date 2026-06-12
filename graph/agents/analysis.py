import re
from langchain_core.messages import AIMessage
from graph.state import AgentState
from graph.tools.python_repl import run_python_code
from graph.llm import get_llm

def analysis_node(state: AgentState) -> dict:
    """
    Analysis Agent Node.
    Reads the research output, determines if quantitative computations are required,
    executes Python code in a safe REPL capture, and synthesizes analytical findings.
    
    Args:
        state (AgentState): Current graph state.
        
    Returns:
        dict: Updated state dictionary with analysis_output.
    """
    task = state.get("task", "")
    research_output = state.get("research_output", "")
    
    llm = get_llm()
    
    # 1. Prompt LLM to analyze research and write python code if calculations are needed
    prompt = (
        "You are the Analysis Agent. Your job is to crunch numbers, compare options, "
        "and draw conclusions based on the research findings.\n"
        f"Task: \"{task}\"\n\n"
        f"--- Research Agent Output ---\n{research_output}\n\n"
        "If you need to run mathematical computations, simulations, or logic checks, "
        "format the code block precisely as:\n"
        "```python\n"
        "# your code here\n"
        "print(result)\n"
        "```\n"
        "If code is not needed, simply write your complete analytical conclusions."
    )
    
    response = llm.invoke(prompt)
    analysis_text = response.content
    
    # 2. Parse and execute code block if generated
    code_match = re.search(r"```python(.*?)```", analysis_text, re.DOTALL)
    if code_match:
        code_to_run = code_match.group(1).strip()
        execution_result = run_python_code(code_to_run)
        
        # 3. Supply execution output back to LLM to get final analysis report
        prompt_refine = (
            "You are the Analysis Agent. The code you wrote was executed with the following output:\n"
            f"--- Code ---\n{code_to_run}\n\n"
            f"--- Execution Output ---\n{execution_result}\n\n"
            "Using this calculated data and the original research, write your final "
            "Analysis Report with clear figures, metrics, and quantitative conclusions."
        )
        response_refine = llm.invoke(prompt_refine)
        analysis_report = response_refine.content
    else:
        analysis_report = analysis_text
        
    return {
        "analysis_output": analysis_report,
        "messages": [AIMessage(content=f"**Analysis Agent Report**:\n{analysis_report}", name="AnalysisAgent")]
    }

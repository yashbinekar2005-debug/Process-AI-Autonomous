import sys
import io
import traceback

def run_python_code(code: str) -> str:
    """
    Executes Python code and returns standard output and error.
    
    Args:
        code (str): The python code to execute.
        
    Returns:
        str: Captured stdout, stderr, or traceback error.
    """
    # Clean up markdown code blocks if the LLM included them
    if code.strip().startswith("```python"):
        code = code.strip().split("```python", 1)[1]
    elif code.strip().startswith("```"):
        code = code.strip().split("```", 1)[1]
        
    if code.strip().endswith("```"):
        code = code.strip().rsplit("```", 1)[0]
        
    code = code.strip()

    # Capture stdout and stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = io.StringIO()
    redirected_error = io.StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_error
    
    local_vars = {}
    global_vars = {}
    
    try:
        exec(code, global_vars, local_vars)
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
        output = redirected_output.getvalue()
        error = redirected_error.getvalue()
        
        result_parts = []
        if output:
            result_parts.append(output)
        if error:
            result_parts.append(f"Stderr:\n{error}")
            
        if not result_parts:
            # Check if there's any last statement value we can show
            return "Code executed successfully with no stdout."
            
        return "\n".join(result_parts)
    except Exception as e:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        return f"Execution Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

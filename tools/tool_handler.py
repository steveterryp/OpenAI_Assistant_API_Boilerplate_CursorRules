import json
from functools import lru_cache
from .file_tools import read_file, write_file, list_files
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Dict, Any, Optional
from openai.types.beta.threads import Run

# Cache the function mapping
@lru_cache(maxsize=1)
def get_function_map():
    return {
        "read_file": read_file,
        "write_file": write_file,
        "list_files": list_files,
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def handle_tool_calls(run: Run) -> List[Dict[str, Any]]:
    """
    Handle tool calls from the assistant.
    
    Args:
        run (Run): The current run object from OpenAI
        
    Returns:
        List[Dict[str, Any]]: List of tool outputs
        
    Raises:
        ValueError: If tool execution fails
    """
    tool_outputs = []
    function_map = get_function_map()
    
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name in function_map:
            try:
                output = function_map[function_name](**function_args)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
            except Exception as e:
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": f"Error executing {function_name}: {str(e)}"
                })
    
    return tool_outputs
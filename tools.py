import os
import json

AGENT_DIRECTORY = "agent_directory"

def ensure_agent_directory():
    """Ensure the agent directory exists."""
    if not os.path.exists(AGENT_DIRECTORY):
        os.makedirs(AGENT_DIRECTORY)

def read_file(file_path):
    """Read a file from the agent directory."""
    full_path = os.path.join(AGENT_DIRECTORY, file_path)
    try:
        with open(full_path, 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path, content=""):
    """Write content to a file in the agent directory."""
    ensure_agent_directory()
    full_path = os.path.join(AGENT_DIRECTORY, file_path)
    try:
        with open(full_path, 'w') as file:
            file.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_files():
    """List all files in the agent directory."""
    ensure_agent_directory()
    try:
        files = os.listdir(AGENT_DIRECTORY)
        return json.dumps(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def get_tool_definitions():
    """Return the list of tool definitions for the assistant."""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file from the working directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The name of the file to read (will be read from the working directory)"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file in the working directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The name of the file to write (will be created in the working directory)"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List files in the working directory",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }
    ]

def handle_tool_calls(run):
    """Handle tool calls from the assistant."""
    tool_outputs = []
    
    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        output = None
        if function_name == "read_file":
            output = read_file(function_args["file_path"])
        elif function_name == "write_file":
            # Add default empty content if not provided
            content = function_args.get("content", "")
            output = write_file(function_args["file_path"], content)
        elif function_name == "list_files":
            output = list_files()
            
        if output is not None:
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": output
            })
    
    return tool_outputs

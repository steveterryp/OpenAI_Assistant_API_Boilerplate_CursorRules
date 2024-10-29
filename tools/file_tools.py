import os
import json
from functools import lru_cache

AGENT_DIRECTORY = "agent_directory"

# Cache the directory check
@lru_cache(maxsize=1)
def get_agent_directory():
    """Get or create the agent directory."""
    if not os.path.exists(AGENT_DIRECTORY):
        os.makedirs(AGENT_DIRECTORY)
    return AGENT_DIRECTORY

def get_full_path(file_path):
    """Get the full path for a file."""
    return os.path.join(get_agent_directory(), file_path)

def read_file(file_path):
    """Read a file from the agent directory."""
    try:
        with open(get_full_path(file_path), 'r') as file:
            return file.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_file(file_path, content=""):
    """Write content to a file in the agent directory."""
    try:
        with open(get_full_path(file_path), 'w') as file:
            file.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def list_files():
    """List all files in the agent directory."""
    try:
        files = os.listdir(get_agent_directory())
        return json.dumps(files)
    except Exception as e:
        return f"Error listing files: {str(e)}"
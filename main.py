import os
from openai import OpenAI
from dotenv import load_dotenv
from tools import handle_tool_calls, get_tool_definitions  
from terminalstyle import (
    print_assistant_response,
    print_system_message,
    print_code,
    clear_screen,
    print_welcome_message,
    print_divider,
    get_user_input,
    print_tool_usage,
)
from prompts import SUPER_ASSISTANT_INSTRUCTIONS

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and Assistant ID from environment variables
api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# File to store the thread ID
THREAD_ID_FILE = "thread_id.txt"

def load_thread_id():
    """Load the thread ID from a file, if it exists."""
    if os.path.exists(THREAD_ID_FILE):
        with open(THREAD_ID_FILE, "r") as file:
            return file.read().strip()
    return None

def save_thread_id(thread_id):
    """Save the thread ID to a file."""
    with open(THREAD_ID_FILE, "w") as file:
        file.write(thread_id)

def create_assistant(client):
    """Create an assistant with the specified tools."""
    assistant = client.beta.assistants.create(
        name="Super Assistant",
        instructions=SUPER_ASSISTANT_INSTRUCTIONS,
        model="gpt-4o-mini",
        tools=get_tool_definitions()  # Get tools from tools.py
    )
    return assistant

def wait_for_completion(client, thread_id, run_id):
    """Wait for a run to complete and handle any required actions."""
    while True:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        
        if run.status == "requires_action":
            tool_outputs = handle_tool_calls(run)
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                print_tool_usage(tool_call.function.name)
            run = client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=tool_outputs
            )
        elif run.status == "completed":
            return run
        elif run.status in ["failed", "cancelled", "expired"]:
            print_system_message(f"Run ended with status: {run.status}")
            return None

def cancel_active_runs(client, thread_id):
    """Cancel any active runs on the thread."""
    try:
        runs = client.beta.threads.runs.list(thread_id=thread_id)
        for run in runs.data:
            if run.status in ["in_progress", "queued", "requires_action"]:
                try:
                    client.beta.threads.runs.cancel(
                        thread_id=thread_id,
                        run_id=run.id
                    )
                except Exception:
                    pass  # Ignore errors in cancellation
    except Exception:
        pass  # Ignore errors in listing runs

def main():
    thread_id = load_thread_id()
    assistant = create_assistant(client)

    clear_screen()
    print_welcome_message()
    print_divider()

    while True:
        user_input = get_user_input()

        if user_input.lower() == "reset":
            if thread_id:
                cancel_active_runs(client, thread_id)  # Cancel any active runs before reset
            thread_id = None
            if os.path.exists(THREAD_ID_FILE):
                os.remove(THREAD_ID_FILE)
            print_system_message("Thread reset. Starting a new conversation.")
            print_divider()
            continue

        if user_input.lower() == "quit":
            if thread_id:
                cancel_active_runs(client, thread_id)  # Cancel any active runs before quitting
            print_system_message("Thank you for chatting! Goodbye.")
            break

        try:
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id
                save_thread_id(thread_id)
            else:
                # Cancel any active runs before creating a new message
                cancel_active_runs(client, thread_id)

            # Create message
            message = client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input
            )

            # Create run
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant.id
            )

            # Wait for completion
            run = wait_for_completion(client, thread_id, run.id)
            if run is None:
                continue

            # Get messages
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            for message in messages.data:
                if message.role == "assistant":
                    response = message.content[0].text.value
                    print_assistant_response(response)
                    break

        except Exception as e:
            print_system_message(f"An error occurred: {str(e)}")
            print_system_message("Starting a new conversation...")
            if thread_id:
                cancel_active_runs(client, thread_id)  # Cancel any active runs before reset
            thread_id = None
            if os.path.exists(THREAD_ID_FILE):
                os.remove(THREAD_ID_FILE)

        print_divider()

if __name__ == "__main__":
    main()

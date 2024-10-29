# OpenAI_Assistant_API_Boilerplate

Super simple boilerplate for using the OpenAI Assistant API + Cursor Rules for you to start building personal AI Agents

## How to use

1. Clone the repository:
   ```
   git clone https://github.com/ali-abassi/OpenAI_Assistant_API_Boilerplate.git
   ```

2. Change `.SAMPLEenv` to `.env` and add your API keys:
   - Open the `.env` file
   - Add your OpenAI API Key
   - Add your Assistant ID

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the script:
   ```
   python main.py
   ```

5. Start chatting with your personal assistant!

6. Use the cursor composer to start adding your own tools along with documentation details from the apis you want to use. Use the attached `AddTools_CursorInstructions.md` to help you.

## Features

- OpenAI Assistant API integration
- File operations (read/write)
- Rich terminal interface
- Conversation persistence so it recalls your prior convos until you tell it to 'reset'

# LLM.py

import google.generativeai as genai
import json
import os
import config  # Import your config file
import voice_output # Import speak for error reporting

# Load system prompt (assuming it's in a standard location)
SYSTEM_PROMPT_PATH = "Jarvis/config/SYSTEM_PROMPT.txt" # Adjust path if needed

def initialize_llm(api_key: str, model_name: str):
    """Initializes the Google Generative AI model and chat."""
    print(f"Initializing LLM: {model_name}...")
    if not api_key:
        raise ValueError("Google_API_KEY not found in config.py or is empty.")

    try:
        genai.configure(api_key=api_key)
        print("✅ Gemini API Configured")

        # --- Load System Prompt ---
        try:
            with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as file:
                system_prompt = file.read()
            initial_history = [
                {"role": "user", "parts": [system_prompt]},
                {"role": "model", "parts": ["Understood. I am Jarvis, ready to assist. How can I help you today?"]} # Initial model response
            ]
            print(f"✅ System prompt loaded from {SYSTEM_PROMPT_PATH}")
        except FileNotFoundError:
            print(f"⚠️ Warning: System prompt file not found at {SYSTEM_PROMPT_PATH}. Proceeding without it.")
            initial_history = [] # Start with no history if prompt is missing
        except Exception as e:
            print(f"🔴 Error loading system prompt: {e}. Proceeding without it.")
            initial_history = []

        # --- Model Initialization ---
        model = genai.GenerativeModel(model_name)
        # Start a chat session for conversation history
        chat = model.start_chat(history=initial_history)
        print(f"✅ Initialized Gemini Model: {model_name} with chat history.")
        return chat, model

    except Exception as e:
        print(f"🔴 LLM Initialization failed: {e}")
        raise RuntimeError(f"LLM Initialization failed: {e}") from e

def llm_parser(chat_session, command):
    """
    Sends the command to the LLM and parses the JSON response.

    Args:
        chat_session: The initialized Gemini chat session.
        command: The user's command (string or list with image).
        tts_stream: The TTS stream object for speaking errors.

    Returns:
        The parsed JSON object (dict) or None if an error occurs.
    """
    if not chat_session:
        print("🔴 Error: LLM chat session not initialized.")
        return None

    print(f"➡️ Sending to LLM: {command if isinstance(command, str) else command[0] + ' <image>'}") # Don't print full image data
    response = chat_session.send_message(command)
    answer = response.text
    print(f"💬 LLM Response Raw: {answer}") # Log the raw response

    # Clean the response to extract JSON
    # Handle potential markdown code blocks ```json ... ``` or just ``` ... ```
    json_str = answer.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.startswith("```"):
            json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    json_str = json_str.strip() # Remove leading/trailing whitespace

    # Parse the cleaned JSON string
    parsed_data = json.loads(json_str)
    print(f"✅ LLM Response Parsed: {parsed_data}")
    return parsed_data
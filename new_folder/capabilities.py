# capabilities.py

import os
import datetime
import requests
import sys
import json
import time
import pyautogui
import pywhatkit
from PIL import Image
import asyncio
import traceback # For detailed error logging

# Assuming your feature modules are in a 'Jarvis/features' subdirectory
# Adjust imports if your structure is different
try:
    from Jarvis.features import date_time
    from Jarvis.features import launch_app
    from Jarvis.features import website_open
    from Jarvis.features import weather
    from Jarvis.features import wikipedia
    # from Jarvis.features import news # Removed
    from Jarvis.features import send_email
    from Jarvis.features import google_search
    # from Jarvis.features import google_calendar # Uncomment if you have this module
    from Jarvis.features import note
    from Jarvis.features import system_stats
    from Jarvis.features import loc
    from Jarvis.features import browser_use # Your browser automation module
    import LLM # Import LLM module for describe_screen dependency
except ImportError as e:
    print(f"🔴 Error importing feature module or LLM: {e}")
    print("Ensure the 'Jarvis/features' directory and LLM.py exist and are accessible.")
    sys.exit(1) # Exit if core dependencies are missing

import config # Import your config file
# Only execute_command will import voice_output now
# import voice_output # No longer needed here

# --- List of Available Function Names (Strings) ---
AVAILABLE_FUNCTIONS = [
    "tell_me_date",
    "tell_time",
    "launch_any_app",
    "website_opener",
    "weather",
    "tell_me",
    "send_mail",
    "search_anything_google",
    "play_music",
    "youtube",
    "where_is",
    "my_location",
    "take_screenshot",
    "show_screenshot",
    "system_info",
    "ip_address",
    "switch_window",
    "take_note",
    "close_note",
    "describe_screen",
    "browser_use",
    "goodbye"
]

# --- Jarvis Assistant Class ---
class JarvisAssistant:
    """
    Encapsulates the core functionalities (capabilities) of Jarvis.
    All public methods intended to be called by the LLM *must* return a string
    which is the message Jarvis should speak.
    """
    def __init__(self, model_name, email_user, email_pass):
        print("Initializing Jarvis Capabilities...")
        self.model_name = model_name
        self.email_username = email_user
        self.email_password = email_pass
        self.screenshot_name = None
        print("✅ Jarvis Capabilities Initialized.")

    # --- Capability Methods (Return strings only) ---

    def tell_me_date(self) -> str:
        """Returns the current date as a string."""
        return date_time.date()

    def tell_time(self) -> str:
        """Returns the current time as a formatted string."""
        time_c = date_time.time()
        return f"Sir, the time is {time_c}"

    def launch_any_app(self, app_name: str) -> str:
        """Tries to launch an app and returns a status string."""
        app_name_lower = app_name.lower()
        path = config.APP_PATHS.get(app_name_lower)
        if path and os.path.exists(path):
            print(f"Launching {app_name} from path: {path}")
            try:
                success = launch_app.launch_app(path)
                return f"Launching {app_name} for you sir!" if success else f"Failed to launch {app_name}."
            except Exception as e:
                print(f"Error launching app {app_name}: {e}")
                return f"Sorry sir, I encountered an error trying to launch {app_name}."
        elif path:
            print(f"Error: Path found for '{app_name}' but does not exist: {path}")
            return f"Sorry sir, I found the path for {app_name}, but it seems invalid."
        else:
             print(f"Application '{app_name}' not found in config.APP_PATHS.")
             return f"Sorry sir, I don't have the path for {app_name} configured."

    def website_opener(self, domain: str) -> str:
        """Tries to open a website and returns a confirmation string."""
        domain_cleaned = domain.replace("https://", "").replace("http://", "").replace("www.", "")
        if '.' not in domain_cleaned and ' ' not in domain_cleaned:
             domain_cleaned += ".com"
        print(f"Opening website: {domain_cleaned}")
        try:
            website_open.website_opener(domain_cleaned)
            return f"Alright sir! Opening {domain_cleaned}"
        except Exception as e:
            print(f"Error opening website {domain_cleaned}: {e}")
            return f"Sorry sir, I couldn't open the website {domain_cleaned}."

    def weather(self, city: str) -> str:
        """Fetches weather and returns the info or an error string."""
        print(f"Fetching weather for: {city}")
        try:
            res = weather.fetch_weather(city)
            return res if res else f"Sorry sir, I couldn't fetch the weather information for {city}."
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return "Sorry sir, an error occurred while fetching the weather."

    def tell_me(self, topic: str) -> str:
        """Gets Wikipedia info and returns it or an error string."""
        print(f"Searching Wikipedia for: {topic}")
        try:
            res = wikipedia.tell_me_about(topic)
            return res if res else f"Sorry sir, I couldn't find information about {topic} on Wikipedia."
        except Exception as e:
            print(f"Error fetching Wikipedia info for {topic}: {e}")
            return f"Sorry sir, an error occurred while looking up {topic}."

    def send_mail(self, recipient_name: str, subject: str, message: str) -> str:
        """Tries to send an email and returns a status string."""
        recipient_name_lower = recipient_name.lower()
        receiver_email = config.EMAIL_DIC.get(recipient_name_lower)

        if not self.email_username or not self.email_password:
             print("Error: Email credentials not configured in config.py")
             return "Sorry sir, my email sending capability is not configured."

        if receiver_email:
            print(f"Preparing email to {recipient_name} ({receiver_email})")
            msg_body = f'Subject: {subject}\n\n{message}'
            try:
                success = send_email.mail(self.email_username, self.email_password,
                                          receiver_email, msg_body)
                return "Email has been successfully sent." if success else "Sorry sir. Couldn't send your mail. Please check the logs."
            except Exception as e:
                print(f"Error sending email: {e}")
                return "Sorry sir. An unexpected error occurred while sending your mail."
        else:
            print(f"Recipient '{recipient_name}' not found in EMAIL_DIC.")
            return f"I couldn't find {recipient_name}'s email in my database. Please add it to the configuration."

    def search_anything_google(self, query: str) -> str:
        """Performs a Google search and returns a confirmation string."""
        print(f"Searching Google for: {query}")
        try:
            google_search.google_search(query)
            return f"Searching Google for {query}."
        except Exception as e:
            print(f"Error performing Google search: {e}")
            return "Sorry sir, I encountered an error while searching Google."

    def play_music(self) -> str:
        """Tries to play music and returns a status string."""
        music_dir = config.MUSIC_DIR
        print(f"Attempting to play music from: {music_dir}")
        if not music_dir or not os.path.isdir(music_dir):
            print("Error: Music directory not configured or invalid in config.py")
            return "Sorry sir, the music directory is not set up correctly."
        try:
            songs = [s for s in os.listdir(music_dir) if s.lower().endswith(('.mp3', '.wav', '.flac'))]
            if not songs:
                return f"Sorry sir, I couldn't find any music files in {music_dir}."

            song_to_play = os.path.join(music_dir, songs[0])
            print(f"Playing: {songs[0]}")
            os.startfile(song_to_play)
            song_name_cleaned = songs[0].split('.')[0].replace('_', ' ')
            return f"Now playing {song_name_cleaned}."
        except Exception as e:
            print(f"Error playing music: {e}")
            return "Sorry sir, I encountered an error while trying to play music."

    def youtube(self, video_query: str) -> str:
        """Tries to play a YouTube video and returns a status string."""
        print(f"Searching YouTube for: {video_query}")
        try:
            pywhatkit.playonyt(video_query)
            return f"Playing {video_query} on YouTube."
        except Exception as e:
            print(f"Error playing YouTube video: {e}")
            return "Sorry sir, I couldn't play the video on YouTube. Please check your internet connection."

    def where_is(self, place: str) -> str:
        """Gets location info and returns it or an error string."""
        print(f"Looking up location: {place}")
        try:
            current_loc, target_loc, distance = loc.loc(place)
            if not target_loc:
                 return f"Sorry sir, I couldn't find the location {place}."

            city = target_loc.get('city', '')
            state = target_loc.get('state', '')
            country = target_loc.get('country', '')

            if city:
                res = f"{place} is in {state} state, {country}. It is approximately {distance} km away from your current location."
            elif state:
                 res = f"{state} is a state in {country}. It is approximately {distance} km away from your current location."
            else:
                 res = f"I found {country} for {place}, but couldn't get specific city/state details. It's about {distance} km away."

            print(res)
            return res
        except Exception as e:
            print(f"Error getting location: {e}")
            return "Sorry sir, I encountered an error while looking up the location."

    def my_location(self) -> str:
        """Gets current location and returns it or an error string."""
        print("Fetching current location...")
        try:
            city, state, country = loc.my_location()
            res = f"You are currently located in {city}, {state}, {country}."
            print(res)
            return res
        except Exception as e:
            print(f"Error fetching current location: {e}")
            return "Sorry sir, I couldn't fetch your current location."

    def take_screenshot(self, name: str = "screenshot") -> str:
        """Takes a screenshot and returns a status string."""
        save_dir = config.SCREENSHOT_DIR
        if not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
                print(f"Created screenshot directory: {save_dir}")
            except OSError as e:
                print(f"Error creating screenshot directory {save_dir}: {e}")
                return f"Sorry sir, I couldn't create the directory to save the screenshot: {save_dir}"

        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '_')).rstrip()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{timestamp}.png"
        full_path = os.path.join(save_dir, filename)

        print(f"Taking screenshot and saving to: {full_path}")
        try:
            img = pyautogui.screenshot()
            img.save(full_path)
            self.screenshot_name = full_path
            return f"Screenshot saved as {filename}."
        except Exception as e:
            print(f"Error taking screenshot: {e}")
            return "Sorry sir, I encountered an error while taking the screenshot."

    def show_screenshot(self) -> str:
        """Tries to show the last screenshot and returns a status string."""
        if not self.screenshot_name:
            return "Sorry sir, I haven't taken a screenshot recently to show."
        print(f"Showing screenshot: {self.screenshot_name}")
        try:
            if os.path.exists(self.screenshot_name):
                img = Image.open(self.screenshot_name)
                img.show()
                return "Here is the last screenshot."
            else:
                 return "Sorry sir, I remember taking a screenshot, but I can't find the file anymore."
        except Exception as e:
            print(f"Error showing screenshot: {e}")
            return "Sorry sir, I encountered an error while trying to display the screenshot."

    def system_info(self) -> str:
        """Gets system stats and returns them or an error string."""
        print("Fetching system info...")
        try:
            # Assuming system_stats.system_stats() returns a string
            return system_stats.system_stats()
        except Exception as e:
            print(f"Error getting system info: {e}")
            return "Sorry sir, I couldn't retrieve the system information."

    def ip_address(self) -> str:
        """Gets public IP and returns it or an error string."""
        print("Fetching IP address...")
        try:
            ip = requests.get('https://api.ipify.org').text
            print(f"IP Address: {ip}")
            return f"Your public IP address is {ip}."
        except requests.exceptions.RequestException as e:
            print(f"Error fetching IP address: {e}")
            return "Sorry sir, I couldn't fetch the IP address. Please check your internet connection."

    def switch_window(self) -> str:
        """Switches window and returns a confirmation string."""
        print("Switching window (Alt+Tab)...")
        try:
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            time.sleep(0.5)
            pyautogui.keyUp("alt")
            return "Switched window."
        except Exception as e:
            print(f"Error switching window: {e}")
            return "Sorry sir, I encountered an error while trying to switch windows."

    def take_note(self, note_text: str) -> str:
        """Takes a note and returns a confirmation string."""
        print(f"Taking note: {note_text}")
        try:
            note.note(note_text) # Assuming note.note() handles file I/O
            return "I've made a note of that."
        except Exception as e:
            print(f"Error taking note: {e}")
            return "Sorry sir, I encountered an error while taking the note."

    def close_note(self) -> str:
        """Tries to close notepad and returns a status string."""
        app_to_close = "notepad++.exe" # Or "notepad.exe"
        print(f"Attempting to close {app_to_close}...")
        try:
            if sys.platform == "win32":
                # Use '> nul 2>&1' to suppress command output
                result_check = os.system(f'tasklist /fi "imagename eq {app_to_close}" | find /i "{app_to_close}" > nul 2>&1')
                if result_check != 0: # Not running
                    return f"{app_to_close} doesn't seem to be running."
                else:
                    result = os.system(f"taskkill /f /im {app_to_close} > nul 2>&1")
                    return f"Closed {app_to_close}." if result == 0 else f"Sorry sir, I couldn't close {app_to_close}. It might require administrator privileges."
            else: # Basic Linux/macOS attempt
                # Check if running first (less reliable cross-platform)
                # result_check = os.system(f"pgrep -f {app_to_close.split('.')[0]} > /dev/null 2>&1")
                # if result_check != 0:
                #      return f"{app_to_close} doesn't seem to be running."
                result = os.system(f"pkill -f {app_to_close.split('.')[0]}")
                return f"Attempted to close {app_to_close}." if result == 0 else f"Sorry sir, I couldn't close {app_to_close} using pkill."
        except Exception as e:
            print(f"Error closing note application: {e}")
            return f"Sorry sir, an error occurred while trying to close {app_to_close}."

    def describe_screen(self, llm_chat_session, tts_stream) -> str:
        """Captures screen, asks LLM, and returns the description or error string."""
        print("Capturing screen for description...")
        try:
            img = pyautogui.screenshot()
            prompt = "Describe this screenshot in detail. What application or window is primarily visible? What elements can you identify?"
            contents = [prompt, img]

            print(f"➡️ Sending image and prompt to LLM for description...")
            # We still need tts_stream for the LLM parser's internal error speaking
            # Modify LLM.llm_parser if you want to prevent *any* speaking outside execute_command
            parsed_response = LLM.llm_parser(llm_chat_session, contents, tts_stream)

            if parsed_response and parsed_response.get("answer"):
                return parsed_response["answer"]
            else:
                 # If LLM parser failed or didn't return an answer
                 print("LLM did not return a valid description.")
                 # LLM.llm_parser might have already spoken an error via tts_stream
                 # Return a generic error string from this function's perspective
                 return "Sorry, I wasn't able to get a description of the screen."

        except Exception as e:
            print(f"\n🔴 Error describing screen: {e}")
            return "Sorry sir, I encountered an error while processing the screenshot for description."

    async def _run_browser_task(self, task_description):
        """Internal async helper for browser task."""
        # This should return the final result string from the browser agent
        return await browser_use.browser_use(task_description, self.model_name)

    def browser_use(self, task_description: str) -> str:
        """Runs the browser task and returns the final result string."""
        print(f"Starting browser task: {task_description}")
        # Confirmation speaking is removed from here and execute_command
        # The final result string will be spoken by execute_command
        try:
            # Run the async function
            result = asyncio.run(self._run_browser_task(task_description))
            print(f"Browser task completed. Result: {result}")
            # Return the result string obtained from the browser agent
            return f"Browser task finished. Result: {result}"
        except ImportError:
             print("🔴 Error: Langchain/Browser components not installed or found.")
             return "Sorry sir, the browser automation components seem to be missing."
        except Exception as e:
            print(f"🔴 Error during browser task execution: {e}")
            traceback.print_exc()
            return "Sorry sir, I encountered an error while performing the browser task."

    def goodbye(self) -> str:
        """Returns the farewell message string."""
        return "Alright sir, going offline. It was nice working with you."


# --- Command Execution Logic (Handles Speaking) ---
def execute_command(parsed_data: dict, assistant: JarvisAssistant, tts_stream, xllm_chat_session):
    """
    Executes the appropriate JarvisAssistant method dynamically and speaks the result.

    Args:
        parsed_data (dict): The JSON object from the LLM parser.
        assistant (JarvisAssistant): The instance of the capabilities class.
        tts_stream: The TTS stream for speaking results.
        llm_chat_session: The LLM chat session (needed for describe_screen).

    Returns:
        bool: True if the 'goodbye' command was issued, False otherwise.
    """
    # Import here to keep JarvisAssistant class clean
    import voice_output

    function_name = parsed_data.get("function_name")
    args = parsed_data.get("args", [])
    answer = parsed_data.get("answer") # Direct answer from LLM

    result_message = None # String to be spoken
    should_shutdown = False

    # 1. Handle direct answers from LLM
    if not function_name and answer:
        result_message = answer

    # 2. Handle function calls if function_name is valid
    elif function_name in AVAILABLE_FUNCTIONS:
        try:
            method_to_call = getattr(assistant, function_name)
            print(f"Dynamically executing function: {function_name} with args: {args}")

            # --- Handle Special Cases ---
            if function_name == "describe_screen":
                # Needs extra args not from LLM's 'args' list
                # The method itself now returns the string to speak
                result_message = method_to_call(llm_chat_session, tts_stream)

            elif function_name == "goodbye":
                result_message = method_to_call() # Gets the farewell string
                should_shutdown = True # Set flag

            # --- Handle General Case ---
            else:
                if args:
                    result_message = method_to_call(*args)
                else:
                    result_message = method_to_call()

        except AttributeError:
            print(f"🔴 Error: Function '{function_name}' in AVAILABLE_FUNCTIONS but not found in JarvisAssistant class.")
            result_message = f"Sorry, there's an internal mismatch for the command '{function_name}'."
        except TypeError as e:
             print(f"🔴 TypeError executing '{function_name}' with args {args}: {e}")
             traceback.print_exc()
             result_message = f"Sorry sir, there was an issue with the arguments provided for the {function_name.replace('_', ' ')} command."
        except Exception as e:
            print(f"🔴🔴 An error occurred executing '{function_name}': {e}")
            traceback.print_exc()
            result_message = f"Sorry, I encountered an unexpected error while trying to {function_name.replace('_', ' ')}."

    # 3. Handle invalid function names provided by LLM
    elif function_name:
        print(f"⚠️ Unknown or disallowed function called by LLM: {function_name}")
        result_message = f"Sorry sir, I recognized the command '{function_name}' but it's not an available action."

    # 4. Handle cases where LLM failed completely
    else: # function_name is None and answer is None
         result_message = "Sorry sir, I couldn't understand your request. Please try again."

    # 5. Speak the final result message
    if result_message: # Only speak if there's something to say
        # Speak goodbye synchronously before returning True
        is_sync = should_shutdown
        voice_output.speak(tts_stream, result_message, synchronous=is_sync)
    elif not result_message and function_name == "describe_screen":
        # If describe_screen failed and returned None, we already printed an error.
        # No need to speak an additional generic error unless desired.
        pass # Or speak a generic error: voice_output.speak(tts_stream, "Sorry, I couldn't describe the screen.")

    return should_shutdown
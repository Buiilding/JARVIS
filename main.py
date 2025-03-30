# Jarvis Imports (retained)
from Jarvis import JarvisAssistant
import re
import os
import random
import pprint
import datetime
import requests
import sys
import urllib.parse
import pyjokes
import time
import pyautogui
import pywhatkit
import wolframalpha
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
from Jarvis.config import config # Assuming config holds wolframalpha_id and potentially email creds

# Realtime STT/TTS Imports
import signal
from RealtimeTTS import TextToAudioStream, EdgeEngine
from RealtimeSTT import AudioToTextRecorder

load_dotenv() # Load variables from .env file

# --- Global Variables ---
stream = None
recorder = None
engine = None
obj = None # JarvisAssistant object

# ================================ MEMORY (from original Jarvis) ==================================
GREETINGS = ["hello jarvis", "jarvis", "wake up jarvis", "you there jarvis", "time to work jarvis", "hey jarvis", 
             "ok jarvis", "are you there?"]
GREETINGS_RES = ["always there for you sir", "i am ready sir",
                 "your wish my command", "how can i help you sir?", "i am online and ready sir"]

EMAIL_DIC = {
    'myself': 'peterbuics@gmail.com', # Replace with actual emails or load securely
    'my official email': 'peterbuics@gmail.com',
    'my second email': 'peterbuics@gmail.com',
    'my official mail': 'peterbuics@gmail.com',
    'my second mail': 'peterbuics@gmail.com'
}

CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
# ================================================================================================

# --- New TTS Function ---
def speak(text):
    """ Uses RealtimeTTS to speak the given text. """
    global stream
    if stream:
        print(f"🤖 Jarvis: {text}") # Print what Jarvis is saying
        try:
            stream.feed(text)
            # Optional: Add a small pause after feeding text if needed
            stream.feed(" ") # Add a space to ensure buffer flush/trigger playback
            if not stream.is_playing():
                stream.play_async()
        except Exception as e:
            print(f"🔴 Error in TTS feeding/playback: {e}")
    else:
        print("🔴 Error: TTS Stream not initialized.")
        print(f"(Would have spoken: {text})") # Fallback print

# --- Gemini API Configuration ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    print("🔴 Error: GOOGLE_API_KEY not found in environment variables.")
    print("   Please create a .env file with GOOGLE_API_KEY=\"YOUR_API_KEY\"")
    sys.exit(1)

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Gemini API Configured")
except Exception as e:
    print(f"🔴 Gemini configuration failed: {e}")
    sys.exit(1)

# --- Model Initialization ---
# Choose your Gemini model (e.g., 'gemini-1.5-flash', 'gemini-pro')
MODEL_NAME = 'gemini-1.5-flash'
with open("Jarvis/config/SYSTEM_PROMPT.txt", "r", encoding="utf-8") as file:
    SYSTEM_PROMPT = file.read()
initial_history = [
        {
            "role": "user",
            "parts": [SYSTEM_PROMPT]
        },
    ]
try:
    model = genai.GenerativeModel(MODEL_NAME)
    # Start a chat session for conversation history
    chat = model.start_chat(history=initial_history) # Gemini uses its own history management
    print(f"✅ Initialized Gemini Model: {MODEL_NAME}")
except Exception as e:
    print(f"🔴 Failed to initialize Gemini model: {e}")
    sys.exit(1)

print(f"✅ Initialized Gemini Model: {MODEL_NAME} with Jarvis persona and instructions.")

# --- Startup Function (modified to use new speak) ---
def startup():
    """ Initial greeting and status check. """
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour <= 12:
        speak("Good Morning Sir")
    elif 12 < hour < 18:
        speak("Good afternoon Sir")
    else:
        speak("Good evening Sir")

    # Check internet connection (basic check)
    try:
        requests.get("https://google.com", timeout=5)
        speak("Internet connection is active.")
        print("✅ Internet Connection Active")
    except requests.ConnectionError:
        print("⚠️  Warning: No internet connection.")
        speak("Warning, I cannot connect to the internet.")

    c_time = obj.tell_time()
    speak(f"Currently it is {c_time}")
    time.sleep(3)
    speak("I am Jarvis. Online and ready sir. How may I help you?")

# --- Signal Handler (from real-time script) ---
def signal_handler(sig, frame):
    """ Handles Ctrl+C for graceful shutdown. """
    print("\nShutting down gracefully...")
    global stream, recorder
    if stream and stream.is_playing():
        print("Stopping TTS stream...")
        stream.stop()
    if recorder:
        print("Stopping STT recorder...")
        recorder.stop()
        time.sleep(1)
    print("Goodbye!")
    sys.exit(1)

# --- Function to parse command into LLM ---
def LLM_parser(command):
    """ Parses the command into a LLM for it to determine which function to call. """
    answer = ""
    try:
        response = chat.send_message(command)
        answer = response.text
        print(f"💬 LLM Response: {answer}")
        return answer
    except Exception as e:
        print(f"🔴 Error in LLM parsing: {e}")
        speak("Sorry sir, I encountered an error in the Large Language Model while processing your request.")
        return None
# --- Command Processing Function (Callback for STT) ---
def process_command(text):
    """
    This function is called when RealtimeSTT detects speech.
    It stops any ongoing TTS and processes the command using Jarvis logic.
    """
    global stream, obj

    # 1. Stop any currently playing TTS output (Interruption)
    if stream and stream.is_playing():
        print("--- TTS Interrupted ---")
        stream.stop()

    if not text:
        print("Empty input received, listening again...")
        return # Ignore empty input

    command = text # Get the command from the detected speech
    print(f"\n👤 User: {command}")

    json_str = LLM_parser(command) # Call the LLM parser to determine the function to call
    # Template: "{"function_name": function_name, "args": [arg1, arg2, ...]}"
    # Convert json_str to a JSON object
    import json
    try:
        # Use json.loads() to parse a JSON string ('s' for string)
        parsed_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        try:
            json_str = json_str.replace("`", '')
            json_str = json_str.replace("json", '')
            parsed_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            speak("Sorry sir, I could not convert the string to the json object.")
            print(f"Error decoding JSON from LLM: {e}")
            print(f"Original LLM output string was: {json_str}")
            return
        except Exception as e:
            print(f"An unexpected error occurred while parsing JSON: {e}")
            speak("Sorry sir, I encountered an unexpected error while processing your request.")
            return
        # Handle the error - maybe ask the LLM again or provide a default response
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return

    function_name = parsed_data.get("function_name")
    args = parsed_data.get("args", [])
    # Check if function_name is None or empty
    if not function_name:
        answer = parsed_data.get("answer")
        if answer:
            speak(answer)
            print(answer)
        else:
            speak("Sorry sir, I couldn't understand your request. Please try again.")
        return

    try :
        if function_name == "tell_me_date":
            date = obj.tell_me_date()
            print(date)
            speak(date)
        elif function_name == "tell_time":
            time_c = obj.tell_time()
            print(time_c)
            speak(f"Sir the time is {time_c}")
        elif function_name == "launch_any_app":
            app = args[0]
            dict_app = {
                'chrome': 'C:/Program Files/Google/Chrome/Application/chrome'
            }

            path = dict_app.get(app)

            if path is None:
                speak('Application path not found')
                print('Application path not found')

            else:
                speak('Launching: ' + app + ' for you sir!')
                obj.launch_any_app(path_of_app=path)
        elif function_name == "website_opener":
            domain = args[0]
            open_result = obj.website_opener(domain)
            speak(f'Alright sir !! Opening {domain}')
            print(open_result)
        elif function_name == "weather":
            city = args[0]
            weather_res = obj.weather(city=city)
            print(weather_res)
            speak(weather_res)
        elif function_name == "tell_me":
            topic = args[0]
            if topic:
                wiki_res = obj.tell_me(topic)
                print(wiki_res)
                speak(wiki_res)
            else:
                speak(
                    "Sorry sir. I couldn't load your query from my database. Please try again")
        elif function_name == "news":
            news_res = obj.news()
            speak('Source: The Times Of India')
            speak('Todays Headlines are..')
            for index, articles in enumerate(news_res):
                pprint.pprint(articles['title'])
                speak(articles['title'])
                if index == len(news_res)-2:
                    break
            speak('These were the top headlines, Have a nice day Sir!!..')
        elif function_name == "search_anything_google":
            search_query = args[0]
            print(f"Searching Google for: {search_query}")
            speak(f"Searching Google for {search_query}")
            obj.search_anything_google(search_query)
        elif function_name == "play_music":
            music_dir = "F://Songs//Imagine_Dragons"
            songs = os.listdir(music_dir)
            for song in songs:
                os.startfile(os.path.join(music_dir, song))
        elif function_name == "youtube":
            video = args[0]
            speak(f"Okay sir, playing {video} on youtube")
            pywhatkit.playonyt(video)
        elif function_name == "send_mail":
            sender_email = config.email
            sender_password = config.email_password

            try:
                recipient = args[0]
                receiver_email = EMAIL_DIC.get(recipient)
                if receiver_email:

                    subject = args[1]
                    message = args[2]
                    msg = 'Subject: {}\n\n{}'.format(subject, message)
                    obj.send_mail(sender_email, sender_password,
                                    receiver_email, msg)
                    speak("Email has been successfully sent")
                    time.sleep(2)

                else:
                    speak(
                        "I coudn't find the requested person's email in my database. Please try again with a different name")

            except:
                speak("Sorry sir. Couldn't send your mail. Please try again")
        # elif function_name == "calculate":
        #     question = args[0]
        #     answer = computational_intelligence(question)
        #     speak(answer)
        elif function_name == "where_is":
            place = args[0]
            current_loc, target_loc, distance = obj.location(place)
            city = target_loc.get('city', '')
            state = target_loc.get('state', '')
            country = target_loc.get('country', '')
            time.sleep(1)
            try:

                if city:
                    res = f"{place} is in {state} state and country {country}. It is {distance} km away from your current location"
                    print(res)
                    speak(res)

                else:
                    res = f"{state} is a state in {country}. It is {distance} km away from your current location"
                    print(res)
                    speak(res)

            except:
                res = "Sorry sir, I couldn't get the co-ordinates of the location you requested. Please try again"
                speak(res)
        elif function_name == "my_location":
            try:
                city, state, country = obj.my_location()
                print(city, state, country)
                speak(
                    f"You are currently in {city} city which is in {state} state and country {country}")
            except Exception as e:
                speak(
                    "Sorry sir, I coundn't fetch your current location. Please try again")
        elif function_name == "take_screenshot":
            name = args[0]
            speak("Alright sir, taking the screenshot")
            img = pyautogui.screenshot()
            name = f"{name}.png"
            img.save(name)
            speak("The screenshot has been succesfully captured")
        elif function_name == "show_screenshot":
            try:
                img = Image.open('D://JARVIS//JARVIS_2.0//' + name)
                img.show(img)
                speak("Here it is sir")
                time.sleep(2)

            except IOError:
                speak("Sorry sir, I am unable to display the screenshot")
        elif function_name == "get_joke":
            joke = pyjokes.get_joke()
            print(joke)
            speak(joke)
        elif function_name == "system_info":
            sys_info = obj.system_info()
            print(sys_info)
            speak(sys_info)
        elif function_name == "ip_address":
            ip = requests.get('https://api.ipify.org').text
            print(ip)
            speak(f"Your ip address is {ip}")
        elif function_name == "switch_window":
            speak("Okay sir, Switching the window")
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            time.sleep(1)
            pyautogui.keyUp("alt")
        elif function_name == "take_note":
            note_text = args[0]
            obj.take_note(note_text)
            speak("I've made a note of that")
        elif function_name == "close_note":
            speak("Okay sir, closing notepad")
            os.system("taskkill /f /im notepad++.exe")
        elif function_name == "describe_screen":
            img = pyautogui.screenshot()
            prompt = "Describe this screenshot in detail. What application or window is primarily visible?"

            # Prepare the content list for the API call
            # The API directly accepts PIL Image objects
            contents = [prompt, img]

            print(f"➡️ Sending image and prompt ('{prompt}') to {MODEL_NAME}...")
            try:
                # Use chat.send_message for conversational context
                response = chat.send_message(contents)
                response = response.text
                response = response.replace("`", '')
                response = response.replace("json", '')
                response = response.replace("{", '')
                response = response.replace("}", '')
                response = response.replace('"answer": ', '')
                speak(response)
            except Exception as e:
                print(f"\n🔴 Error sending content to Gemini: {e}")
                speak("Sorry sir, I encountered an error while processing the screenshot.")
                return
        elif function_name == "goodbye":
            speak("Alright sir, going offline. It was nice working with you")
            if stream: # Check if stream exists and is valid
                while stream.is_playing():
                    try:
                        # Sleep briefly to avoid consuming 100% CPU while waiting
                        time.sleep(0.1)
                    except KeyboardInterrupt:
                        print("\nShutdown interrupted while waiting for speech.")
                        # Optionally perform minimal cleanup or just exit
                        sys.exit(1) # Exit immediately if interrupted here
            signal_handler(signal.SIGINT, None)
            sys.exit(1) # Exit the program
    except Exception as e:
        # Catch-all for errors during command processing
        print(f"🔴🔴 An error occurred processing command '{command}': {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback for debugging
        speak("Sorry, I encountered an unexpected error while processing your request.")

# --- Main Execution ---
if __name__ == "__main__":
    # 1. Register Signal Handler
    signal.signal(signal.SIGINT, signal_handler)

    print("🚀 Initializing Jarvis...")

    try:
        obj = JarvisAssistant()
        print("✅ Jarvis Assistant Initialized")

        try:
            engine = EdgeEngine(rate = 20) # Use default settings or specify rate/pitch/volume
            stream = TextToAudioStream(engine, log_characters=False) # Set log_characters=True for debug if needed
            desired_voice_id = "en-US-SteffanNeural"

            engine.set_voice(desired_voice_id)
            print("✅ TTS Engine Initialized")
        except Exception as e:
            print(f"🔴 Fatal Error Initializing TTS: {e}")
            sys.exit(1)

        try:
            recorder = AudioToTextRecorder(
                language="en",         # Explicitly english
                spinner=False,         # Cleaner output
            )
            print("✅ STT Recorder Initialized")
        except Exception as e:
            print(f"🔴 Fatal Error Initializing STT: {e}")
            sys.exit(1)

        startup() # Uses the new speak function

        # 6. Start Listening Loop
        print("\n🟢 Jarvis is listening. Speak your command...")
        print("   (Press Ctrl+C to exit)")
        while True:
            try:
                # recorder.text() blocks until a sentence is detected
                recorder.text(process_command)
            except KeyboardInterrupt:
                 # This might be caught here or by the signal handler
                 print("\nCtrl+C detected during listening loop.")
                 signal_handler(signal.SIGINT, None)
            except Exception as e:
                 # Catch errors within the listening loop itself (rare)
                 print(f"\n🔴 An error occurred in the main listening loop: {e}")
                 traceback.print_exc()
                 # Optionally try to recover or just exit
                 speak("A critical error occurred in my listening module. I might need to restart.")
                 time.sleep(3)
                 signal_handler(None, None) # Attempt graceful shutdown

    except KeyboardInterrupt:
        # Handle Ctrl+C during initialization phase
        print("\nCtrl+C detected during initialization.")
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        # Catch any other unexpected error during initialization
        print(f"\n🔴🔴 A fatal error occurred during Jarvis initialization: {e}")
        import traceback
        traceback.print_exc()
        # Attempt cleanup even if initialization failed partially
        if stream and stream.is_playing(): stream.stop()
        if recorder: recorder.stop()
        sys.exit(1) # Exit with error code
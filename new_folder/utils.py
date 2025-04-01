# utils.py

import os
import signal
import time
import datetime
import sys

# Import necessary components from other modules
import voice_output
import voice_input

def startup(tts_stream):
    """ Initial greeting based on the time of day. """
    hour = int(datetime.datetime.now().hour)
    greeting = "Hello Sir" # Default
    if 0 <= hour < 12:
        greeting = "Good Morning Sir"
    elif 12 <= hour < 18:
        greeting = "Good afternoon Sir"
    else:
        greeting = "Good evening Sir"
    voice_output.speak(tts_stream, greeting)
    # Optional: Add a status check message
    # voice_output.speak(tts_stream, "All systems nominal.")

def signal_handler(sig, frame, tts_stream, stt_recorder, jarvis_instance):
    """ Handles Ctrl+C or planned shutdown for graceful exit. """
    # Prevent running multiple times if signals come quickly
    if jarvis_instance.is_shutting_down:
        print("Shutdown already in progress...")
        return
    jarvis_instance.is_shutting_down = True # Set the flag

    print("\nShutting down gracefully...")

    # 1. Stop TTS playback immediately
    voice_output.stop_tts(tts_stream)

    # 2. Stop STT Recorder
    voice_input.stop_stt(stt_recorder)

    # 3. Optional: Add any other cleanup (e.g., close browser agent if running)

    print("Goodbye!")
    os._exit(0) # Force exit after cleanup
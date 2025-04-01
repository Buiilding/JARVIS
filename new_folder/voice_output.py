# voice_output.py

import time
from RealtimeTTS import TextToAudioStream, EdgeEngine

def initialize_tts(voice_id="en-US-SteffanNeural", rate=50):
    """Initializes the TTS engine and stream."""
    print("Initializing TTS Engine...")
    try:
        engine = EdgeEngine(rate=rate) # Use default settings or specify rate/pitch/volume
        engine.set_voice(voice_id)
        stream = TextToAudioStream(engine, log_characters=False) # Set log_characters=True for debug
        print(f"✅ TTS Engine Initialized (Voice: {voice_id})")
        return stream, engine
    except Exception as e:
        print(f"🔴 Fatal Error Initializing TTS: {e}")
        # Consider raising the exception or returning None to signal failure
        raise RuntimeError(f"TTS Initialization failed: {e}") from e

def speak(stream: TextToAudioStream, text: str, synchronous: bool = False):
    """
    Uses the initialized RealtimeTTS stream to speak the given text.

    Args:
        stream: The initialized TextToAudioStream object.
        text: The text to be spoken.
        synchronous: If True, block until speaking is finished.
                     Useful for farewell messages before exiting.
    """
    if not stream:
        print("🔴 Error: TTS Stream not available.")
        print(f"(Would have spoken: {text})")
        return

    print(f"🤖 Jarvis: {text}") # Print what Jarvis is saying
    try:
        stream.feed(text)
        # Add a space to help ensure buffer flush/trigger playback, especially for short text
        stream.feed(" ")
        if synchronous:
            # Wait for the stream to finish playing the current buffer
            print("Speaking synchronously...")
            while stream.is_playing():
                time.sleep(0.1)
            print("Synchronous speaking finished.")
        elif not stream.is_playing():
             # Start playback if not already playing (async)
            stream.play_async()
    except Exception as e:
        print(f"🔴 Error in TTS feeding/playback: {e}")

def stop_tts(stream: TextToAudioStream):
    """Stops any ongoing TTS playback."""
    if stream and stream.is_playing():
        print("--- Stopping TTS ---")
        stream.stop()
        time.sleep(0.2) # Give it a moment to fully stop
# voice_input.py

import time
from RealtimeSTT import AudioToTextRecorder

def initialize_stt(language="en", spinner=False):
    """Initializes the STT recorder."""
    print("Initializing STT Recorder...")
    try:
        recorder = AudioToTextRecorder(
            language=language,
            spinner=spinner,
        )
        print("✅ STT Recorder Initialized")
        return recorder
    except Exception as e:
        print(f"🔴 Fatal Error Initializing STT: {e}")
        raise RuntimeError(f"STT Initialization failed: {e}") from e

def start_listening(recorder: AudioToTextRecorder, callback_func):
    """
    Starts the STT recorder and calls the callback function when text is detected.
    This function blocks until interrupted.
    """
    if not recorder:
        print("🔴 Error: STT Recorder not initialized.")
        return

    print("\n🟢 Jarvis is listening. Speak your command...")
    print("   (Press Ctrl+C to exit)")
    while True: # Keep listening indefinitely
        try:
            # recorder.text() blocks until a sentence is detected, then calls the callback
            recorder.text(callback_func)
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt caught in listening loop.")
            # The signal handler should take over from here.
            # We break the loop just in case, but the handler usually exits.
            break
        except Exception as e:
            # Catch errors within the listening loop itself (e.g., microphone issues)
            print(f"\n🔴 An error occurred in the STT listening loop: {e}")
            import traceback
            traceback.print_exc()
            # Attempt to recover or inform the user
            # For simplicity here, we'll just print and continue the loop
            # In a more robust system, you might try re-initializing or exiting
            print("Attempting to continue listening...")
            time.sleep(2)


def stop_stt(recorder: AudioToTextRecorder):
    """Stops the STT recorder."""
    if recorder:
        print("Stopping STT recorder...")
        recorder.stop()
        print("Giving recorder a moment to finalize...")
        time.sleep(1.5) # Allow threads to clean up
# main.py

import signal
import time
import sys
import traceback

# Import your modules
import config
import voice_input
import voice_output
import LLM
import capabilities
import utils

class Jarvis:
    """Main Jarvis application class."""

    def __init__(self):
        """Initialize all components."""
        print("🚀 Initializing Jarvis...")
        self.is_shutting_down = False
        self.tts_stream = None
        self.tts_engine = None
        self.stt_recorder = None
        self.llm_chat = None
        self.llm_model = None
        self.assistant = None

        try:
            # 1. Initialize TTS
            self.tts_stream, self.tts_engine = voice_output.initialize_tts(
                # voice_id="...", # Optional: specify voice from config or here
                # rate=config.TTS_RATE # Optional: specify rate
            )

            # 2. Initialize STT
            self.stt_recorder = voice_input.initialize_stt(
                # language=config.STT_LANGUAGE # Optional
            )

            # 3. Initialize LLM
            self.llm_chat, self.llm_model = LLM.initialize_llm(
                api_key=config.Google_API_KEY,
                model_name=config.GOOGLE_LLM_MODEL
            )

            # 4. Initialize Capabilities (JarvisAssistant)
            self.assistant = capabilities.JarvisAssistant(
                model_name=config.GOOGLE_LLM_MODEL,
                email_user=config.email_username,
                email_pass=config.email_password
            )

            print("✅ Jarvis Initialization Complete.")

        except Exception as e:
            print(f"\n🔴🔴 A fatal error occurred during Jarvis initialization: {e}")
            traceback.print_exc()
            # Attempt partial cleanup if possible
            if self.tts_stream: voice_output.stop_tts(self.tts_stream)
            if self.stt_recorder: voice_input.stop_stt(self.stt_recorder)
            sys.exit(1) # Exit with error code

    def process_command(self, text: str):
        """
        Callback function for STT. Processes the detected text.
        """
        if self.is_shutting_down:
            print("Shutdown in progress, ignoring final callback.")
            return

        # 1. Stop any currently playing TTS output (Interruption)
        if self.tts_stream and self.tts_stream.is_playing():
            print("--- TTS Interrupted ---")
            self.tts_stream.stop() # Use the stop function for clarity

        if not text:
            print("Empty input received, listening again...")
            return # Ignore empty input

        command = text.strip()
        print(f"\n👤 User: {command}")

        # 2. Parse command using LLM
        parsed_data = LLM.llm_parser(self.llm_chat, command)

        # 3. Execute command if parsing was successful
        if parsed_data:
            should_shutdown = capabilities.execute_command(
                parsed_data,
                self.assistant,
                self.tts_stream,
                self.llm_chat # Pass chat session for capabilities like describe_screen
            )
            if should_shutdown:
                # The 'goodbye' command was handled, initiate shutdown sequence
                # signal_handler will be called via the registered signal or manually
                # We don't call shutdown directly here to keep signal handling central
                print("Shutdown initiated by 'goodbye' command.")
                # Trigger the signal handler manually for a clean exit path
                self.shutdown_signal_handler(signal.SIGINT, None)
        else:
            # llm_parser or execute_command already spoke the error
            print("Command processing failed or was invalid.")


    def shutdown_signal_handler(self, sig, frame):
        """Wrapper to call the utility signal handler with instance context."""
        # Pass necessary components to the utility handler
        utils.signal_handler(sig, frame, self.tts_stream, self.stt_recorder, self)


    def run(self):
        """Starts Jarvis: registers signal handler, greets, starts listening."""
        # 1. Register Signal Handler for Ctrl+C
        signal.signal(signal.SIGINT, self.shutdown_signal_handler)

        # 2. Startup Greeting
        utils.startup(self.tts_stream)

        # 3. Start Listening Loop (this blocks)
        try:
            voice_input.start_listening(self.stt_recorder, self.process_command)
        except Exception as e:
            # Catch unexpected errors during the main run phase
            print(f"\n🔴🔴 A critical error occurred during runtime: {e}")
            traceback.print_exc()
            voice_output.speak(self.tts_stream, "A critical error occurred. I need to shut down.", synchronous=True)
            # Trigger shutdown
            self.shutdown_signal_handler(None, None) # Pass None for sig/frame if not from signal


# --- Main Execution ---
if __name__ == "__main__":
    try:
        jarvis = Jarvis()
        jarvis.run()
    except KeyboardInterrupt:
        # This might catch Ctrl+C during the very initial setup in __main__
        print("\nCtrl+C detected during script startup. Exiting.")
        # No cleanup needed here as Jarvis object might not be fully initialized
        sys.exit(0)
    except Exception as e:
        # Catch errors during Jarvis class instantiation
        print(f"\n🔴🔴 Failed to instantiate Jarvis: {e}")
        traceback.print_exc()
        sys.exit(1)
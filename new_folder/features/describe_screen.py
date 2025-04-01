import pyautogui
def describe_screen(self, llm_parser_func: callable):
    """
    Takes a screenshot and uses the provided LLM parser function
    to describe it. The LLM Provider needs to handle image input.
    """
    print("--- Capturing screen for description ---")
    try:
        img = pyautogui.screenshot()
        prompt = "Describe this screenshot in detail. What application or window is primarily visible? What elements can you identify?"

        # The LLM provider needs to be able to handle this format: [prompt, image]
        contents = [prompt, img]

        # Call the LLM parser function passed from the main Jarvis class
        parsed_data = llm_parser_func(contents)

        if parsed_data and parsed_data.get("answer"):
            return parsed_data["answer"]
        elif parsed_data:
                # If LLM returned a function call instead of answer
                return "The language model tried to call a function instead of describing the screen. Please try asking again."
        else:
                return "Sorry, I received no description from the language model."

    except Exception as e:
        print(f"\n🔴 Error during screen description: {e}")
        import traceback
        traceback.print_exc()
        return "Sorry sir, I encountered an error while processing the screenshot."
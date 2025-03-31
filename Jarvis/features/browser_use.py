
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent # Ensure browser_use.py and Agent class are accessible
from dotenv import load_dotenv
load_dotenv()
# <<< --- New Async Function for Browser Agent --- >>>
async def browser_use(task: str, model_name: str = "gemini-2.0-flash"):
    """
    Initializes and runs the browser_use Agent asynchronously.
    """
    print(f"--- Starting Browser Agent for task: {task} ---")
    try:
        # Initialize the LLM specifically for the agent
        # Using the same model as the main Jarvis logic
        agent_llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)

        agent = Agent(
            task=task,
            llm=agent_llm,
        )
        # The agent likely prints its own progress/results during run()
        await agent.run()
        print("--- Browser Agent finished task ---")
        return agent.state.last_result[0].extracted_content
        # Optional: Modify Agent class to return a summary string if needed
        # return summary
    except Exception as e:
        print(f"🔴 Error running browser agent: {e}")
        # Optionally return an error message
        # return f"Error during browser task: {e}"
        raise # Re-raise the exception to be caught in process_command
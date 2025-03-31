from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    agent = Agent(
        task="search for the capital of France",
        llm=ChatGoogleGenerativeAI(model = "gemini-2.0-flash"),
    )
    await agent.run()
    result = agent.state.last_result[0].extracted_content
    print(result)


asyncio.run(main())
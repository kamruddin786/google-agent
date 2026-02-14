import os
from datetime import datetime
from google.adk.agents.llm_agent import Agent
from google.adk.models.lite_llm import LiteLlm

from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

tavily=TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_web(query: str):
    """Searches the web for up-to-date information."""
    response = tavily.search(query=query, search_depth="basic")
    return response['results']

def get_current_time() -> dict:
    """Returns the current date and time"""
    now = datetime.now()
    formattted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": formattted_time}

# MODEL=LiteLlm(model="ollama_chat/llama3.2:1b")
MODEL=LiteLlm(model="ollama_chat/ministral-3:8b")


root_agent = Agent(
    model=MODEL,
    name='root_agent',
    # description='A helpful assistant for user questions.',
    description='A helpful assistant for user questions. Use tools as needed.',
    instruction='Answer user questions to the best of your knowledge, Use search_web for up-to-date information.',
    # instruction='Answer user questions to the best of your knowledge',
    tools=[search_web,get_current_time]
)

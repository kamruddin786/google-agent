import os
from datetime import datetime
from google.adk.agents.llm_agent import Agent

from tavily import TavilyClient
from dotenv import load_dotenv

from simple_agent.config import MODEL
from simple_agent.financial_advisor.advisor_agent import financial_advisor_agent

load_dotenv()

_tavily_client = None


def _get_tavily():
    """Lazy-initialise the Tavily client so the API key is read at call time."""
    global _tavily_client
    if _tavily_client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError("TAVILY_API_KEY is not set in the environment.")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def search_web(query: str):
    """Searches the web for up-to-date information."""
    tavily = _get_tavily()
    response = tavily.search(query=query, search_depth="basic")
    return response['results']


def get_current_time() -> dict:
    """Returns the current date and time"""
    now = datetime.now()
    formattted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": formattted_time}


root_agent = Agent(
    model=MODEL,
    name='root_agent',
    description='A helpful assistant for user questions. Delegates financial and investment queries to the financial advisor.',
    instruction=(
        'Answer user questions to the best of your knowledge. '
        'Use search_web for up-to-date general information. '
        'For any questions about stocks, mutual funds, investments, portfolio, '
        'or financial markets, delegate to the financial_advisor_agent.'
    ),
    tools=[search_web, get_current_time],
    sub_agents=[financial_advisor_agent],
)

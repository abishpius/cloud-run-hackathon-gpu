import os

from google.adk.agents import Agent
from dotenv import load_dotenv
from .prompts import SPECIALIST_AGENT_PROMPT

load_dotenv()

from google.adk.tools import google_search

specialist_agent = Agent(
    name="specialist_referral_agent",
    model=os.getenv("SPECIALIST_AGENT_MODEL", "gemini-2.5-flash"),
    instruction=SPECIALIST_AGENT_PROMPT,
    tools=[google_search],
)

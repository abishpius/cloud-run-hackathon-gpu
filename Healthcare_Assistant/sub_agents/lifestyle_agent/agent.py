import os

from google.adk.agents import Agent
from dotenv import load_dotenv
from .prompts import LIFESTYLE_AGENT_PROMPT

load_dotenv()

lifestyle_agent = Agent(
    name="lifestyle_prevention_agent",
    model=os.getenv("LIFESTYLE_AGENT_MODEL", 'gemini-2.5-Flash'), 
    instruction=LIFESTYLE_AGENT_PROMPT,

)

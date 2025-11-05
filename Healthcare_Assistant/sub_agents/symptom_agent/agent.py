import os

from google.adk.agents import Agent
from dotenv import load_dotenv
from .prompts import SYMPTOM_AGENT_PROMPT

load_dotenv()


symptom_agent = Agent(
    name="symptom_analysis_agent",
    model=os.getenv("SYMPTOM_AGENT_MODEL", 'gemini-2.5-Flash'),
    instruction=SYMPTOM_AGENT_PROMPT,
)
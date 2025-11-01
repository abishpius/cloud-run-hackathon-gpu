import os

from google.adk.agents import Agent
from dotenv import load_dotenv
from .prompts import MEDICATIONS_AGENT_PROMPT

load_dotenv()


med_interaction_agent = Agent(
    name="medication_interaction_agent",
    model=os.getenv("MEDICATIONS_AGENT_MODEL", 'Gemini-2.5-Flash'),
    instruction=MEDICATIONS_AGENT_PROMPT,
)

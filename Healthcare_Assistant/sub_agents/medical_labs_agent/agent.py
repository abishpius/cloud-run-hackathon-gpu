import os

from google.adk.agents import Agent
from dotenv import load_dotenv
from .prompts import MEDICAL_LABS_AGENT_PROMPT

load_dotenv()

lab_agent = Agent(
    name="lab_result_interpreter_agent",
    model=os.getenv("MEDICAL_LABS_AGENT_MODEL", 'Gemini-2.5-Flash'),
    instruction=MEDICAL_LABS_AGENT_PROMPT,
)

import os

from google.adk.agents import Agent
from dotenv import load_dotenv
from .prompts import DOCUMENTATION_AGENT_PROMPT
from .tools import deid_tool, store_documentation_firestore

load_dotenv()

documentation_agent = Agent(
    name="clinical_documentation_agent",
    model=os.getenv("DOCUMENTATION_AGENT_MODEL", "gemini-2.5-flash"),
    instruction=DOCUMENTATION_AGENT_PROMPT,
    tools=[deid_tool],
    # Add an after agent callback
    after_agent_callback=store_documentation_firestore
)

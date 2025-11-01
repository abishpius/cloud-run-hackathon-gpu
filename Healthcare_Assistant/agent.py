# --- 1. Imports ---
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, Optional

from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

from .prompt import ROOT_PROMPT
from .sub_agents.symptom_agent.agent import symptom_agent
from .sub_agents.medical_labs_agent.agent import lab_agent
from .sub_agents.medications_agent.agent import med_interaction_agent
from .sub_agents.lifestyle_agent.agent import lifestyle_agent
from .sub_agents.specialist_agent.agent import specialist_agent
from .sub_agents.documentation_agent.agent import documentation_agent

load_dotenv()


# --- 2. Define Schemas ---
class AgentCallMetadata(BaseModel):
    """Tracks which subagents/tools were called and any errors encountered during execution."""
    what_was_called: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping each subagent or tool name to its call status ('success' or 'failed')."
    )
    errors: Dict[str, str] = Field(
        default_factory=dict,
        description="Dictionary mapping each failed subagent/tool to an error message or exception text."
    )


class PrimaryAgentOutput(BaseModel):
    """Structured output returned by the Dr. Cloud Primary Care Agent."""
    patient_summary: str = Field(
        ...,
        description="Patient-facing summary explaining findings, recommendations, and next steps in lay language."
    )
    clinician_summary: str = Field(
        ...,
        description="Clinician-facing summary consolidating subagent outputs, highlighting abnormalities, risks, and recommendations."
    )
    acm: AgentCallMetadata = Field(
        ...,
        description="Audit and call metadata tracking subagent execution status and errors for transparency and debugging."
    )
    metadata: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Optional global metadata such as {'processing_time_ms': '456', 'deidentified': 'true'}."
    )


# --- 3. Configure Agents ---

root_agent = Agent(
    name="dr_cloud_primary_agent",
    model=os.getenv("ROOT_MODEL", "gemini-2.5-flash"),
    instruction=ROOT_PROMPT,
    sub_agents=[
        symptom_agent,
        lab_agent,
        med_interaction_agent,
        lifestyle_agent,
        specialist_agent,
        documentation_agent, 
    ],
    # output_schema=PrimaryAgentOutput,
)

# --- 4. Set up Session Management and Runners ---
# session_service = InMemorySessionService()
# artifact_service = InMemoryArtifactService()

# runner = Runner(
#     agent=root_agent,
#     app_name=os.getenv("APP_NAME", "healthcare_assistant"),
#     session_service=session_service,
#     artifact_service=artifact_service
# )


# --- 1. Imports ---
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, Optional

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCard

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
    model=LiteLlm(model="ollama_chat/medgemma-custom"), #os.getenv("ROOT_MODEL", "gemini-2.5-flash"),
    instruction=ROOT_PROMPT,
    sub_agents=[
        symptom_agent,
        lab_agent,
        med_interaction_agent,
        lifestyle_agent,
        specialist_agent,
        documentation_agent, 
    ],
    # tools = [AgentTool(documentation_agent)],
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


# --- 5. A2A (Agent-to-Agent) Compatibility ---

# Define A2A agent card for healthcare assistant
healthcare_agent_card = AgentCard(
    name="dr_cloud_primary_care_agent",
    url=os.getenv("SERVICE_URL", "http://localhost:8080"),
    description="AI-powered primary care healthcare assistant that analyzes symptoms, interprets lab results, checks medication interactions, provides lifestyle recommendations, suggests specialist referrals, and generates clinical documentation.",
    version="1.0.0",
    capabilities={
        "symptom_analysis": {
            "description": "Analyze patient symptoms and provide differential diagnoses",
            "enabled": True
        },
        "lab_interpretation": {
            "description": "Interpret laboratory results and explain findings",
            "enabled": True
        },
        "medication_interaction": {
            "description": "Check for drug interactions and medication safety",
            "enabled": True
        },
        "lifestyle_recommendations": {
            "description": "Provide personalized health and lifestyle guidance",
            "enabled": True
        },
        "specialist_referral": {
            "description": "Suggest appropriate specialist referrals when needed",
            "enabled": True
        },
        "clinical_documentation": {
            "description": "Generate SOAP/FHIR-compliant clinical documentation",
            "enabled": True
        }
    },
    skills=[
        {
            "name": "symptom_analysis",
            "description": "Analyze symptoms and provide differential diagnoses with risk stratification"
        },
        {
            "name": "lab_results_interpretation",
            "description": "Interpret laboratory test results and explain abnormalities"
        },
        {
            "name": "medication_interaction_check",
            "description": "Check for potential drug interactions and contraindications"
        },
        {
            "name": "lifestyle_guidance",
            "description": "Provide evidence-based lifestyle and wellness recommendations"
        },
        {
            "name": "specialist_referral_recommendation",
            "description": "Recommend appropriate specialist consultations based on symptoms and findings"
        },
        {
            "name": "clinical_note_generation",
            "description": "Generate structured clinical documentation in SOAP or FHIR format"
        }
    ],
    defaultInputModes=["text/plain"],
    defaultOutputModes=["text/plain", "application/json"],
    supportsAuthenticatedExtendedCard=False
)

# Make the agent A2A-compatible
a2a_app = to_a2a(
    root_agent,
    port=int(os.getenv("A2A_PORT", "8001")),
    agent_card=healthcare_agent_card
)


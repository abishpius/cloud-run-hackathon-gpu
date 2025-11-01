import re
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse

from google.cloud import firestore
from datetime import datetime
import uuid
from typing import Optional

import os
from dotenv import load_dotenv
load_dotenv()

def deid_tool(input_text: str) -> str:
    """
    De-identification tool for clinical text or JSON-like strings.
    Removes or masks personally identifiable information (PHI)
    such as names, addresses, phone numbers, emails, dates, and IDs.

    Parameters:
        input_text (str): The raw clinical text or serialized JSON to be scrubbed.

    Returns:
        str: A de-identified version of the input text.
    """
    try:
        # Replace common PHI patterns
        text = input_text

        # Emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', "[REDACTED_EMAIL]", text)
        # Phone numbers
        text = re.sub(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', "[REDACTED_PHONE]", text)
        # Dates
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', "[REDACTED_DATE]", text)
        # Addresses
        text = re.sub(r'\d{1,5}\s[\w\s.,#-]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Blvd|Drive|Dr)\b', "[REDACTED_ADDRESS]", text)
        # MRN / ID-like patterns
        text = re.sub(r'\bMRN[:\s]*\d+\b', "[REDACTED_MRN]", text)
        text = re.sub(r'\bID[:\s]*\d+\b', "[REDACTED_ID]", text)
        # Person names (simple heuristic)
        text = re.sub(r'\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\b', "[REDACTED_NAME]", text)
        
        return text
    
    except Exception as e:
        return input_text

def store_documentation_firestore(callback_context: CallbackContext, llm_response: LlmResponse)-> Optional[LlmResponse]:
    """
    Stores the output of the Clinical Documentation Agent in Firestore.
    
    Parameters:
    - agent: the Agent instance (documentation_agent)
    - context: the current ADK context
    - result: the agent's output dictionary
    """
    try:
        # Connect to Firestore
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "hackathons-461900")
        database_id = os.getenv("FIRESTORE_COLLECTION", "healthcare-assistant")
        db = firestore.Client(project=project_id, database=database_id)

        agent_name = callback_context.agent_name

        # Extract the last user message
        response_text = ""
        for part in llm_response.content.parts:
            if hasattr(part, "text") and part.text:
                response_text += part.text

        if not response_text:
            return None

        # Prepare document data
        doc_id = str(uuid.uuid4())  # unique ID for each note
        data = {
            "timestamp": datetime.utcnow(),
            "agent_name": agent_name,
            "patient_summary": response_text.get("patient_summary")
        }

        # Save to Firestore
        db.collection('patient_health').document(doc_id).set(data)
        print(f"[INFO] Documentation saved to Firestore with ID {doc_id}")
        return None

    except Exception as e:
        print(f"[ERROR] Failed to store documentation: {e}")
        return None  
import re

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

   
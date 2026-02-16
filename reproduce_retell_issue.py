import requests
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = "http://localhost:8000/api/v1/book-appointment"

# The payload from the error log (simplified but structurally representative)
# The key observation is that 'first_name' is missing from root, and there is a 'call' object.
# I will try to structure it as Retell "Include Call Object" usually does: { args: {...}, call: {...} }
# BUT the error log showed 'input': {'call': ...} which implies 'args' MIGHT be missing or I missed it.
# Let's try sending EXACTLY what might be causing the error: a body with just 'call'.
PAYLOAD_JUST_CALL = {
    "call": {
        "call_id": "call_f3f6595bbe94b02bdb706d944d8",
        "agent_id": "agent_1a9912d8eb5a1debae4dcb771d",
        "transcript": "..."
    }
}

# Also try the standard Retell wrapped payload
PAYLOAD_WRAPPED = {
    "args": {
        "doctor_id": "DOC002",
        "first_name": "Kirti",
        "last_name": "Reddy",
        "dob": "1987-06-10",
        "insurance_provider": "Medibody",
        "reason": "Orthopedic consultation - Sports Medicine",
        "requested_datetime": "2026-01-17T10:30:00"
    },
    "call": {
        "call_id": "call_f3f6595bbe94b02bdb706d944d8"
    }
}

def test_payload(name, payload):
    logger.info(f"Testing {name}...")
    try:
        response = requests.post(URL, json=payload)
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text}")
    except Exception as e:
        logger.error(f"Failed: {e}")

if __name__ == "__main__":
    test_payload("Just Call Object", PAYLOAD_JUST_CALL)
    test_payload("Wrapped (args + call)", PAYLOAD_WRAPPED)

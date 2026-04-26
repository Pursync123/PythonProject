import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL_BASE = "http://localhost:8000/api/v1"
URL_BASE = "https://pythonproject-1-e1we.onrender.com/api/v1"

def test_full_flow():
    logger.info(f"--- Diagnosing Remote Environment {URL_BASE} ---")
    
    # 1. Get Doctors
    try:
        resp = requests.get(f"{URL_BASE}/doctors")
        resp.raise_for_status()
        doctors = resp.json().get("doctors", [])
        logger.info(f"Found {len(doctors)} doctors.")
    except Exception as e:
        logger.error(f"Failed to list doctors: {e}")
        return

    # 2. Find Dr. Emily Rodriguez
    target_doctor = None
    for doc in doctors:
        logger.info(f"Doc: {doc['name']} (ID: {doc['id']})")
        if "Emily" in doc['name'] or "Rodriguez" in doc['name']:
            target_doctor = doc
    
    if not target_doctor:
        logger.error("Could not find Dr. Emily Rodriguez")
        # Fallback to first doctor if any
        if doctors:
            target_doctor = doctors[0]
            logger.info(f"Falling back to {target_doctor['name']}")
        else:
            return

    # 3. Get Slots for Doctor
    try:
        # Endpoint is /doctors/{id} which returns { "doctor": { ..., "available_slots": [...] } }
        resp = requests.get(f"{URL_BASE}/doctors/{target_doctor['id']}")
        resp.raise_for_status()
        doc_details = resp.json().get("doctor", {})
        slots = doc_details.get("available_slots", [])
             
        logger.info(f"Found {len(slots)} slots for {target_doctor['name']}")
    except Exception as e:
        logger.error(f"Failed to get slots: {e}")
        return

    # 4. Pick a slot
    if not slots:
        logger.error("No slots available for this doctor.")
        return

    slot = slots[0]
    # Construct requested_datetime from slot
    requested_datetime = f"{slot['date']}T{slot['time']}:00"
    logger.info(f"Attempting valid booking for {requested_datetime}")

    PAYLOAD = {
        "first_name": "Kirti",
        "last_name": "Mary Wedding",
        "dob": "1987-06-10",
        "insurance_provider": "MediBuddy",
        "reason": "Pediatric general health checkup",
        "requested_datetime": requested_datetime,
        "doctor_id": target_doctor['id']
    }
    
    logger.info(f"Payload: {json.dumps(PAYLOAD, indent=2)}")

    try:
        response = requests.post(f"{URL_BASE}/book-appointment", json=PAYLOAD)
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text}")
    except Exception as e:
        logger.error(f"Failed to book: {e}")

if __name__ == "__main__":
    test_full_flow()

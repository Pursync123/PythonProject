import sys
import os
import requests
from datetime import datetime, timedelta

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE_URL = "http://localhost:8001/api/v1"

def create_slot():
    print("--- Testing Slot Creation ---")
    
    # 1. Get a doctor ID
    try:
        resp = requests.get(f"{BASE_URL}/doctors")
        if resp.status_code != 200:
            print(f"Failed to get doctors: {resp.text}")
            return
        
        doctors = resp.json().get("doctors", [])
        if not doctors:
            print("No doctors found to add slot to.")
            return

        doctor_id = doctors[0]['id']
        print(f"Using Doctor ID: {doctor_id}")
        
        # 2. Try to create a slot
        # Using tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        payload = {
            "doctor_id": doctor_id,
            "date": tomorrow,
            "time": "10:15",
            "duration_minutes": 15
        }
        
        print(f"Sending payload: {payload}")
        resp = requests.post(f"{BASE_URL}/doctors/{doctor_id}/slots", json=payload)
        
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {resp.text}")

        if resp.status_code == 200:
            print("✅ Slot created successfully (Unexpected if bug exists)")
        else:
            print("❌ Slot creation failed (Expected behavior)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_slot()

import requests
import json

BASE_URL = "http://localhost:8001/api/v1"

def test_endpoints():
    print(f"Testing endpoints at {BASE_URL}")
    
    # Test Doctors
    try:
        print("\n--- GET /doctors ---")
        resp = requests.get(f"{BASE_URL}/doctors")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Keys: {list(data.keys())}")
            print(f"Count: {data.get('count')}")
            if data.get('doctors'):
                print(f"Sample Doctor: {data['doctors'][0]['name']}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

    # Test Appointments
    try:
        print("\n--- GET /appointments ---")
        resp = requests.get(f"{BASE_URL}/appointments")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Keys: {list(data.keys())}")
            print(f"Count: {data.get('count')}")
            if data.get('appointments'):
                print(f"Sample Appointment ID: {data['appointments'][0]['id']}")
        else:
            print(f"Error: {resp.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_endpoints()

import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.services.doctor_service import DoctorService
from app.schemas.schemas import Doctor as DoctorSchema

def verify_doctors_serialization():
    db = SessionLocal()
    try:
        print("--- Verifying Doctors API Serialization ---")
        
        service = DoctorService(db)
        # matches what get_doctors does
        doctors_data = service.get_all_active_doctors(include_slots=True)
        print(f"Service returned {len(doctors_data)} doctors (dicts with ORM slots)")
        
        if doctors_data:
            print("Attempting Pydantic validation of FIRST doctor...")
            first_doc_data = doctors_data[0]
            try:
                # This simulates what FastAPI would do if we had a response model
                model = DoctorSchema.model_validate(first_doc_data)
                print("✅ Doctor Serialization SUCCESS!")
                print(f"Name: {model.name}, Slots: {len(model.available_slots)}")
            except Exception as e:
                print(f"❌ Doctor Serialization FAILED: {e}")
                import traceback
                traceback.print_exc()

        # Simulate full API response serialization check (raw json dump)
        try:
            print("Attempting naive JSON dump (simulating no response_model)...")
            # This is expected to fail if ORM objects are present
            json.dumps(doctors_data, default=str) 
            # default=str might handle UUIDs/dates but NOT SQLAlchemy objects usually, unless they have __str__? 
            # But SQLAlchemy objects are complex.
            print("⚠️ JSON dump seemingly worked (unexpected if ORM objects presence)")
        except TypeError as e:
            print(f"✅ JSON dump FAILED as expected (caught error): {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_doctors_serialization()

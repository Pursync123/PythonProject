import sys
import os
import json
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.services.appointment_service import AppointmentService
from app.schemas.schemas import AppointmentListResponse, Appointment as PydanticAppointment

def verify_serialization():
    db = SessionLocal()
    try:
        print("--- Verifying API Serialization ---")
        
        service = AppointmentService(db)
        appts = service.get_all_appointments()
        print(f"Service returned {len(appts)} appointments (ORM objects)")
        
        if appts:
            print("Attempting validation of ONE appointment directly...")
            try:
                single_valid = PydanticAppointment.model_validate(appts[0])
                print("✅ Single object validation SUCCESS!")
                print(single_valid)
            except Exception as e:
                print(f"❌ Single object validation FAILED: {e}")
                # import traceback
                # traceback.print_exc()

        # Simulate API Response construction
        response_data = {"status": "success", "appointments": appts, "count": len(appts)}
        
        # Attempt detailed Pydantic validation
        print("Attempting Pydantic validation...")
        try:
            model = AppointmentListResponse.model_validate(response_data)
            print("✅ Serialization SUCCESS!")
            print(f"Serialized {len(model.appointments)} appointments.")
            if model.appointments:
                first = model.appointments[0]
                print(f"Sample: ID={first.id}, Patient={first.patient.first_name}")
        except Exception as e:
            print(f"❌ Serialization FAILED: {e}")
            import traceback
            traceback.print_exc()


    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_serialization()

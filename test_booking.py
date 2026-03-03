import logging
from app.db.session import SessionLocal
from app.services.appointment_service import AppointmentService
from app.schemas.schemas import AppointmentRequest
from datetime import datetime, timedelta
import sys

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def test():
    db = SessionLocal()
    service = AppointmentService(db)
    
    # Calculate a requested datetime 1 day from now at 10:00 AM
    req_datetime = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    
    payload = AppointmentRequest(
        first_name="Test",
        last_name="User",
        dob="1990-01-01",
        phone="1234567890",
        reason="Routine Checkup",
        requested_datetime=req_datetime.isoformat()
    )
    
    try:
        # Note: We are not passing doctor_id here. 
        # The service should find any available doctor for that time.
        logging.info(f"Attempting to book appointment payload: {payload.model_dump()}")
        res = service.book_appointment(payload)
        logging.info(f"Successfully booked appointment: {res}")
    except Exception as e:
        logging.error(f"Failed to book appointment: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test()

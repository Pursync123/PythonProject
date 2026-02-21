import sys
import os
from sqlalchemy import text

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.models import Appointment, AppointmentStatus

def check_appointments():
    db = SessionLocal()
    try:
        print("--- Checking Appointments in DB ---")
        
        # 1. Check total appointments
        total_count = db.query(Appointment).count()
        print(f"Total appointments: {total_count}")
        
        # 2. Check booked appointments (which the API returns)
        booked_count = db.query(Appointment).filter(Appointment.status == AppointmentStatus.BOOKED.value).count()
        print(f"Booked appointments: {booked_count}")
        
        # 3. List all appointments with their status
        appointments = db.query(Appointment).all()
        for appt in appointments:
            print(f"ID: {appt.id}, Patient: {appt.patient_id}, Doctor: {appt.doctor_id}, Status: {appt.status}, Time: {appt.requested_datetime}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_appointments()

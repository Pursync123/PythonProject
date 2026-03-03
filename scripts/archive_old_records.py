import sys
import os
import argparse
from datetime import datetime, timedelta

# Add the project root to the Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.models import (
    Appointment, 
    AvailableSlot, 
    ArchivedAppointment, 
    ArchivedAvailableSlot,
    AppointmentStatus
)

def archive_old_records(days: int = 15):
    """
    Archive appointments and available slots older than the specified number of days.
    """
    db: Session = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        print(f"Archiving records older than {cutoff_date} ({days} days)")

        # ---------------------------------------------------------
        # 1. Archive Old Appointments
        # ---------------------------------------------------------
        old_appointments = db.query(Appointment).filter(
            Appointment.requested_datetime < cutoff_date
        ).all()
        
        archived_appt_count = 0
        for appt in old_appointments:
            # Auto-complete appointments that were left as booked
            final_status = AppointmentStatus.COMPLETED.value if appt.status == AppointmentStatus.BOOKED.value else appt.status
            
            archived_appt = ArchivedAppointment(
                id=appt.id,
                patient_id=appt.patient_id,
                doctor_id=appt.doctor_id,
                slot_id=appt.slot_id,
                reason=appt.reason,
                notes=appt.notes,
                status=final_status,
                requested_datetime=appt.requested_datetime,
                cancelled_at=appt.cancelled_at,
                cancellation_reason=appt.cancellation_reason,
                created_at=appt.created_at,
                updated_at=appt.updated_at,
                archived_at=datetime.utcnow()
            )
            db.add(archived_appt)
            db.delete(appt)
            archived_appt_count += 1
            
        print(f"Archived {archived_appt_count} appointments.")

        # ---------------------------------------------------------
        # 2. Archive Old Available Slots
        # ---------------------------------------------------------
        # Only archive slots that don't have active appointments linked 
        # (since we just moved all old appointments, older slots shouldn't have any active appointments)
        old_slots = db.query(AvailableSlot).filter(
            AvailableSlot.date < cutoff_date.date()
        ).all()

        archived_slot_count = 0
        for slot in old_slots:
            archived_slot = ArchivedAvailableSlot(
                id=slot.id,
                doctor_id=slot.doctor_id,
                date=slot.date,
                time=slot.time,
                duration_minutes=slot.duration_minutes,
                status=slot.status,
                notes=slot.notes,
                created_at=slot.created_at,
                updated_at=slot.updated_at,
                archived_at=datetime.utcnow()
            )
            db.add(archived_slot)
            db.delete(slot)
            archived_slot_count += 1
            
        print(f"Archived {archived_slot_count} available slots.")

        # Commit all changes to the database
        db.commit()
        print("Archive process completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error during archiving process: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archive old database records.")
    parser.add_argument(
        "--days", 
        type=int, 
        default=15, 
        help="Number of days to keep records before archiving (default: 15)"
    )
    args = parser.parse_args()
    archive_old_records(days=args.days)

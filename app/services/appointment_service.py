from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from app.repositories.appointment import AppointmentRepository
from app.repositories.available_slot import AvailableSlotRepository
from app.repositories.doctor import DoctorRepository
from app.repositories.patient import PatientRepository
from app.schemas.schemas import AppointmentRequest
from app.exceptions.custom import SlotUnavailableException, AppointmentNotFoundException, PatientNotFoundException, AppError

class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.appointment_repo = AppointmentRepository(db)
        self.slot_repo = AvailableSlotRepository(db)
        self.doctor_repo = DoctorRepository(db)
        self.patient_repo = PatientRepository(db)
    def book_appointment(self, payload: AppointmentRequest, doctor_id: Optional[str] = None) -> dict:
        """Book an appointment logic"""
        # 1. Check if requested time is in the future
        import pytz
        req_dt = datetime.fromisoformat(payload.requested_datetime.replace("Z", "+00:00"))
        
        # If the datetime is timezone-aware (like from Retell), convert to local time (IST)
        local_tz = pytz.timezone("Asia/Kolkata")
        if req_dt.tzinfo is not None:
            req_dt = req_dt.astimezone(local_tz)
        else:
            # If naive, assume it's already in local time
            req_dt = local_tz.localize(req_dt)
            
        now_local = datetime.now(local_tz)
        if req_dt < now_local:
            raise AppError(
                f"I'm sorry, I can't book an appointment for a past date or time ({payload.requested_datetime}). Could you please suggest a future time?", 
                status_code=400
            )

        # 2. Find Slot
        req_date = req_dt.date()
        req_time = req_dt.time()
        
        selected_slot = None
        if doctor_id:
            selected_slot = self.slot_repo.get_available_slots_by_date_and_time(
                doctor_id, req_date, req_time
            )
        else:
            doctors = self.doctor_repo.get_all_active()
            for doc in doctors:
                selected_slot = self.slot_repo.get_available_slots_by_date_and_time(
                    doc.id, req_date, req_time
                )
                if selected_slot:
                    break
        
        if not selected_slot:
            raise SlotUnavailableException()

        # 3. Create Patient
        patient = self.patient_repo.create(
            first_name=payload.first_name,
            last_name=payload.last_name,
            dob=payload.dob,
            phone=payload.phone
        )

        # 4. Book Slot & Create Appointment
        self.slot_repo.update_status(selected_slot.id, "booked")
        
        # Convert local aware datetime to naive string for DB storage
        naive_local_dt = req_dt.replace(tzinfo=None)
        
        appointment = self.appointment_repo.create(
            patient_id=patient.id,
            doctor_id=selected_slot.doctor_id,
            slot_id=selected_slot.id,
            reason=payload.reason,
            requested_datetime=naive_local_dt,
            status="booked"
        )
        
        return {
            "id": str(appointment.id),
            "doctor_id": appointment.doctor_id,
            "patient": {
                "first_name": patient.first_name,
                "last_name": patient.last_name
            },
            "requested_datetime": str(appointment.requested_datetime)
        }

    def cancel_appointment(self, appointment_id: str):
        try:
            appt_uuid = uuid.UUID(appointment_id)
        except ValueError:
            raise ValueError("Invalid UUID format")

        appt = self.appointment_repo.get_by_id(appt_uuid)
        if not appt:
            raise AppointmentNotFoundException(f"Appointment {appointment_id} not found")

        if appt.status == "cancelled":
            return {"status": "already_cancelled"}

        self.appointment_repo.cancel(appt_uuid)
        
        if appt.slot_id:
            self.slot_repo.update_status(appt.slot_id, "available")
            
        return {"status": "cancelled", "appointment_id": appointment_id}
        
    def get_all_appointments(self):
        """Get all booked appointments"""
        return self.appointment_repo.get_booked_appointments()

    def get_by_id(self, appointment_id: uuid.UUID):
        """Get appointment by ID with error handling"""
        appt = self.appointment_repo.get_by_id(appointment_id)
        if not appt:
            raise AppointmentNotFoundException(f"Appointment {appointment_id} not found")
        return appt




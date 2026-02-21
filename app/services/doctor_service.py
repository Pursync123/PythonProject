from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.doctor import DoctorRepository
from app.repositories.available_slot import AvailableSlotRepository
from app.schemas.schemas import Doctor as DoctorSchema, SlotCreate, SlotUpdate
import uuid

class DoctorService:
    def __init__(self, db: Session):
        self.db = db
        self.doctor_repo = DoctorRepository(db)
        self.slot_repo = AvailableSlotRepository(db)

    def get_all_active_doctors(self, include_slots: bool = False, slot_limit: int = 5, specialization: Optional[str] = None) -> List[dict]:
        """Get all active doctors with optional available slots and specialization filtering"""
        doctors = self.doctor_repo.get_all_active(specialization=specialization)
        result = []
        for doc in doctors:
            doc_data = self._format_doctor(doc, include_slots, slot_limit)
            result.append(doc_data)
        return result

    def get_doctor_by_id(self, doctor_id: str, include_slots: bool = True, slot_limit: int = 20, manage_mode: bool = False) -> Optional[dict]:
        """Get a single doctor by ID with slots"""
        doc = self.doctor_repo.get_by_id(doctor_id)
        if not doc:
            return None
        return self._format_doctor(doc, include_slots, slot_limit, manage_mode)

    def _format_doctor(self, doc, include_slots: bool, slot_limit: int, manage_mode: bool = False) -> dict:
        """Helper to format doctor data"""
        from datetime import date
        today = date.today()
        
        doc_data = {
            "id": doc.id,
            "name": doc.name,
            "department": doc.department,
            "specialization": doc.specialization,
            "experience": doc.experience,
        }
        
        # Filter (available + today/future) and sort by date and time
        if manage_mode:
            # In manage mode, return all future slots regardless of status
            avail_slots = [
                s for s in doc.slots 
                if s.date >= today
            ]
        else:
            # In normal mode, only return available future slots
            avail_slots = [
                s for s in doc.slots 
                if s.status == "available" and s.date >= today
            ]
        avail_slots.sort(key=lambda x: (x.date, x.time))
        
        doc_data["available_slots_count"] = len(avail_slots)
        
        if include_slots:
            doc_data["available_slots"] = avail_slots[:slot_limit]
        
        return doc_data

    def get_available_slots(self, department: Optional[str] = None, slot_limit: int = 10):
        """Get available slots logic with limiting"""
        from datetime import date
        today = date.today()
        
        if department:
            doctors = self.doctor_repo.get_by_department(department)
        else:
            doctors = self.doctor_repo.get_all_active()
        
        result_doctors = []
        for doc in doctors:
            # Filter (available + today/future) and sort by date and time
            avail_slots = [
                s for s in doc.slots 
                if s.status == "available" and s.date >= today
            ]
            avail_slots.sort(key=lambda x: (x.date, x.time))
            
            if avail_slots:
                result_doctors.append({
                    "id": doc.id,
                    "name": doc.name,
                    "department": doc.department,
                    "specialization": doc.specialization,
                    "experience": doc.experience,
                    "available_slots": avail_slots[:slot_limit],
                    "available_slots_count": len(avail_slots)
                })
        return result_doctors

    def create_slot(self, slot_data: SlotCreate):
        """Create a new slot"""
        # Parse date and time if needed, depending on how repo expects it
        # Repo expects date object and time object or string. 
        # API receives strings.
        from datetime import datetime
        
        date_obj = datetime.strptime(slot_data.date, "%Y-%m-%d").date()
        
        # Parse time string to time object
        try:
            time_obj = datetime.strptime(slot_data.time, "%H:%M").time()
        except ValueError:
            try:
                time_obj = datetime.strptime(slot_data.time, "%H:%M:%S").time()
            except ValueError:
                 raise ValueError("Time must be in HH:MM or HH:MM:SS format")

        try:
            return self.slot_repo.create(
                doctor_id=slot_data.doctor_id,
                date_val=date_obj,
                time_val=time_obj,
                duration_minutes=slot_data.duration_minutes
            )
        except Exception as e:
            # Check for IntegrityError (constraint violation)
            error_str = str(e)
            if "IntegrityError" in type(e).__name__ or "UniqueViolation" in error_str:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Slot already exists or conflicts with an existing slot.")
            
            print(f"Error creating slot: {e}")
            import traceback
            traceback.print_exc()
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail="Internal Server Error during slot creation.")

    def update_slot_status(self, slot_id: str, status: str):
        """Update slot status"""
        return self.slot_repo.update_status(uuid.UUID(slot_id), status)

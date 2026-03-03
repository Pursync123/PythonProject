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
        from datetime import datetime
        now = datetime.now()
        today = now.date()
        current_time = now.time()
        
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
                if s.date > today or (s.date == today and s.time >= current_time)
            ]
        else:
            # In normal mode, only return available future slots
            avail_slots = [
                s for s in doc.slots 
                if s.status == "available" and (s.date > today or (s.date == today and s.time >= current_time))
            ]
        avail_slots.sort(key=lambda x: (x.date, x.time))
        
        doc_data["available_slots_count"] = len(avail_slots)
        
        if include_slots:
            doc_data["available_slots"] = avail_slots[:slot_limit]
        
        return doc_data

    def get_available_slots(self, department: Optional[str] = None, slot_limit: int = 10):
        """Get available slots logic with limiting"""
        from datetime import datetime
        now = datetime.now()
        today = now.date()
        current_time = now.time()
        
        if department:
            doctors = self.doctor_repo.get_by_department(department)
        else:
            doctors = self.doctor_repo.get_all_active()
        
        result_doctors = []
        for doc in doctors:
            # Filter (available + today/future) and sort by date and time
            avail_slots = [
                s for s in doc.slots 
                if s.status == "available" and (s.date > today or (s.date == today and s.time >= current_time))
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

    def create_bulk_slots(self, data) -> dict:
        """Generate 15-min slots across a date/time range.
        
        Returns dict with created count and skipped count.
        """
        from datetime import datetime, timedelta, date as date_cls, time as time_cls

        start_date = datetime.strptime(data.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(data.end_date, "%Y-%m-%d").date()
        start_time = datetime.strptime(data.start_time, "%H:%M").time()
        end_time = datetime.strptime(data.end_time, "%H:%M").time()
        duration = data.duration_minutes

        if end_date < start_date:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="end_date must be >= start_date")
        if end_time <= start_time:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="end_time must be > start_time")

        # Build the list of slot dicts
        slots_to_create = []
        current_date = start_date
        while current_date <= end_date:
            # Walk the time window in `duration`-minute steps
            slot_dt = datetime.combine(current_date, start_time)
            end_dt = datetime.combine(current_date, end_time)
            while slot_dt + timedelta(minutes=duration) <= end_dt:
                slots_to_create.append({
                    "doctor_id": data.doctor_id,
                    "date": current_date,
                    "time": slot_dt.time(),
                    "duration_minutes": duration,
                })
                slot_dt += timedelta(minutes=duration)
            current_date += timedelta(days=1)

        total = len(slots_to_create)
        created = self.slot_repo.bulk_create(slots_to_create)
        return {"created": created, "skipped": total - created, "total_requested": total}

    def cancel_slots(self, data) -> dict:
        """Cancel/disable slots for a doctor on a date, filtered by period."""
        from datetime import datetime, time as time_cls

        target_date = datetime.strptime(data.date, "%Y-%m-%d").date()
        period = data.period

        # Map period to time boundaries
        if period == "morning":
            start_time = time_cls(0, 0)
            end_time = time_cls(12, 0)
        elif period == "evening":
            start_time = time_cls(12, 0)
            end_time = time_cls(23, 59)
        else:  # "all"
            start_time = None
            end_time = None

        count = self.slot_repo.cancel_slots_in_range(
            doctor_id=data.doctor_id,
            target_date=target_date,
            start_time=start_time,
            end_time=end_time,
        )
        return {"cancelled": count, "date": data.date, "period": period}

    def update_slot_status(self, slot_id: str, status: str):
        """Update slot status"""
        return self.slot_repo.update_status(uuid.UUID(slot_id), status)

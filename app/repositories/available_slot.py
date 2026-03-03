from typing import List, Optional
import uuid
from datetime import datetime, date
from .base import BaseRepository
from app.models.models import AvailableSlot, Doctor, SlotStatus

class AvailableSlotRepository(BaseRepository):
    """Repository for Available Slot operations"""

    def create(self, doctor_id: str, date_val: date, time_val,
               duration_minutes: int = 15, **kwargs) -> AvailableSlot:
        """Create a new available slot"""
        slot = AvailableSlot(
            id=uuid.uuid4(),
            doctor_id=doctor_id,
            date=date_val,
            time=time_val,
            duration_minutes=duration_minutes,
            status=SlotStatus.AVAILABLE.value,
            **kwargs
        )
        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        return slot

    def get_available_slots_by_date_and_time(self, doctor_id: str,
                                             slot_date: date, slot_time) -> Optional[AvailableSlot]:
        """Get available slot for specific date and time"""
        return self.db.query(AvailableSlot).filter(
            AvailableSlot.doctor_id == doctor_id,
            AvailableSlot.date == slot_date,
            AvailableSlot.time == slot_time,
            AvailableSlot.status == SlotStatus.AVAILABLE.value
        ).first()

    def update_status(self, slot_id: uuid.UUID, status: str) -> Optional[AvailableSlot]:
        """Update slot status"""
        slot = self.db.query(AvailableSlot).filter(AvailableSlot.id == slot_id).first()
        if slot:
            slot.status = status
            slot.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(slot)
        return slot
        
    def get_available_slots_by_department(self, department: str) -> List[AvailableSlot]:
        """Get available slots by department"""
        return self.db.query(AvailableSlot).join(Doctor).filter(
            Doctor.department == department,
            AvailableSlot.status == SlotStatus.AVAILABLE.value
        ).order_by(AvailableSlot.date, AvailableSlot.time).all()

    def bulk_create(self, slots_data: List[dict]) -> int:
        """Bulk-insert slots, skipping duplicates by pre-checking existing slots."""
        if not slots_data:
            return 0

        # Collect all dates in this batch to query existing slots once
        dates = list({s["date"] for s in slots_data})
        doctor_id = slots_data[0]["doctor_id"]

        existing = self.db.query(AvailableSlot.date, AvailableSlot.time).filter(
            AvailableSlot.doctor_id == doctor_id,
            AvailableSlot.date.in_(dates),
        ).all()
        existing_set = {(row.date, row.time) for row in existing}

        created = 0
        for s in slots_data:
            key = (s["date"], s["time"])
            if key in existing_set:
                continue  # skip duplicate
            slot = AvailableSlot(
                id=uuid.uuid4(),
                doctor_id=s["doctor_id"],
                date=s["date"],
                time=s["time"],
                duration_minutes=s["duration_minutes"],
                status=SlotStatus.AVAILABLE.value,
            )
            self.db.add(slot)
            existing_set.add(key)  # prevent duplicates within same batch
            created += 1
        self.db.commit()
        return created

    def cancel_slots_in_range(self, doctor_id: str, target_date: date,
                              start_time=None, end_time=None) -> int:
        """Disable all available slots for a doctor on a date, optionally within a time window.
        
        Returns:
            Number of slots cancelled.
        """
        from datetime import time as dt_time
        query = self.db.query(AvailableSlot).filter(
            AvailableSlot.doctor_id == doctor_id,
            AvailableSlot.date == target_date,
            AvailableSlot.status == SlotStatus.AVAILABLE.value,
        )
        if start_time is not None:
            query = query.filter(AvailableSlot.time >= start_time)
        if end_time is not None:
            query = query.filter(AvailableSlot.time < end_time)

        slots = query.all()
        for slot in slots:
            slot.status = SlotStatus.DISABLED.value if hasattr(SlotStatus, 'DISABLED') else "disabled"
            slot.updated_at = datetime.utcnow()
        self.db.commit()
        return len(slots)

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

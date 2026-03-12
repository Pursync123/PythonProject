from typing import List, Optional
import uuid
import logging
from datetime import datetime
from .base import BaseRepository
from app.models.models import Appointment, AppointmentStatus

logger = logging.getLogger(__name__)

class AppointmentRepository(BaseRepository):
    """Repository for Appointment operations"""

    def create(self, patient_id: uuid.UUID, doctor_id: str,
               reason: str, requested_datetime: str, slot_id: Optional[uuid.UUID] = None,
               status: str = AppointmentStatus.BOOKED.value,
               **kwargs) -> Appointment:
        """Create a new appointment"""
        appointment = Appointment(
            id=uuid.uuid4(),
            patient_id=patient_id,
            doctor_id=doctor_id,
            reason=reason,
            requested_datetime=datetime.fromisoformat(requested_datetime) if isinstance(requested_datetime, str) else requested_datetime,
            slot_id=slot_id,
            status=status,
            **kwargs
        )
        self.db.add(appointment)
        self.db.commit()
        self.db.refresh(appointment)
        logger.info(f"Appointment created: {appointment.id}")
        return appointment

    def get_by_id(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        """Get appointment by ID"""
        return self.db.query(Appointment).filter(Appointment.id == appointment_id).first()

    def get_booked_appointments(self) -> List[Appointment]:
        """Get all booked appointments"""
        return self.db.query(Appointment).filter(
            Appointment.status == AppointmentStatus.BOOKED.value
        ).order_by(Appointment.requested_datetime).all()

    def cancel(self, appointment_id: uuid.UUID) -> Optional[Appointment]:
        """Cancel an appointment"""
        appointment = self.get_by_id(appointment_id)
        if appointment:
            appointment.status = AppointmentStatus.CANCELLED.value
            appointment.cancelled_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(appointment)
        return appointment

from typing import Optional
import uuid
import logging
from .base import BaseRepository
from app.models.models import Patient

logger = logging.getLogger(__name__)

class PatientRepository(BaseRepository):
    """Repository for Patient operations"""

    def create(self, first_name: str, last_name: str, dob: str,
               phone: str = None, insurance_provider: str = None, **kwargs) -> Patient:
        """Create a new patient"""
        from datetime import datetime as dt
        dob_date = dt.fromisoformat(dob).date() if isinstance(dob, str) else dob

        patient = Patient(
            id=uuid.uuid4(),
            first_name=first_name,
            last_name=last_name,
            dob=dob_date,
            phone=phone,
            insurance_provider=insurance_provider,
            **kwargs
        )
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        logger.info(f"Patient created: {patient.id}")
        return patient

    def get_by_id(self, patient_id: uuid.UUID) -> Optional[Patient]:
        """Get patient by ID"""
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

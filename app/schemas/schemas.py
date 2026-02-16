from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any
from datetime import date, datetime, time
import uuid

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str  # "BOOK" or "CANCEL"
    appointment_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    details: str

class Patient(BaseModel):
    first_name: str
    last_name: str
    dob: str
    phone: str

class AvailableSlot(BaseModel):
    date: str
    time: str
    duration_minutes: int
    status: str

class Doctor(BaseModel):
    id: str
    name: str
    department: str
    specialization: str
    experience: int
    available_slots: List[AvailableSlot]
    available_slots_count: int

class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient: Patient
    doctor_id: Optional[str] = None # Linking to a doctor if needed, though currently logic binds by time
    reason: str
    requested_datetime: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat() + "Z")
    status: str = "booked" # booked, cancelled

class AppointmentRequest(BaseModel):
    doctor_id: Optional[str] = None
    first_name: str
    last_name: str
    dob: str
    phone: str
    reason: str
    requested_datetime: str

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("dob must be in ISO format YYYY-MM-DD")

    @field_validator("requested_datetime")
    @classmethod
    def validate_requested_datetime(cls, v):
        try:
            datetime.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("requested_datetime must be a valid ISO 8601 datetime string")

    @model_validator(mode='before')
    @classmethod
    def unwrap_retell_args(cls, data: Any) -> Any:
        """
        Retell AI sends function arguments wrapped in an 'args' dictionary.
        This validator unwraps it so the model can validate the inner fields.
        """
        if isinstance(data, dict) and "args" in data:
            return data["args"]
        return data

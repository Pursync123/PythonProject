from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Any
from datetime import date, datetime, time
import uuid

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: str  # "BOOK" or "CANCEL"
    appointment_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    details: str

    model_config = ConfigDict(from_attributes=True)

class Patient(BaseModel):
    first_name: str
    last_name: str
    dob: str | date
    phone: Optional[str] = None



    model_config = ConfigDict(from_attributes=True)

class AvailableSlot(BaseModel):
    id: Optional[str | uuid.UUID] = None # Added ID for updates

    date: date | str
    time: time | str
    duration_minutes: int
    status: str


    model_config = ConfigDict(from_attributes=True)



class SlotCreate(BaseModel):
    doctor_id: str
    date: str
    time: str
    duration_minutes: int = 15

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                datetime.strptime(v, fmt)
                # Ensure we return YYYY-MM-DD for consistency
                return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError("date must be in YYYY-MM-DD or DD-MM-YYYY format")

class SlotUpdate(BaseModel):
    status: str # "available", "booked", "cancelled", "disabled"

    model_config = ConfigDict(from_attributes=True)

class Doctor(BaseModel):
    id: str
    name: str
    department: str
    specialization: str
    experience: int
    available_slots: List[AvailableSlot] = Field(default_factory=list)
    available_slots_count: int

    model_config = ConfigDict(from_attributes=True)

class DoctorListResponse(BaseModel):
    status: str
    count: int
    doctors: List[Doctor]

class DoctorResponse(BaseModel):
    status: str
    doctor: Doctor




class Appointment(BaseModel):
    id: str | uuid.UUID = Field(default_factory=lambda: str(uuid.uuid4()))

    patient: Patient
    doctor_id: Optional[str] = None # Linking to a doctor if needed, though currently logic binds by time
    reason: str
    requested_datetime: datetime | str
    created_at: datetime | str = Field(default_factory=lambda: datetime.now().isoformat() + "Z")

    status: str = "booked" # booked, cancelled

    model_config = ConfigDict(from_attributes=True)



class AppointmentListResponse(BaseModel):
    status: str
    appointments: List[Appointment]
    count: int


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

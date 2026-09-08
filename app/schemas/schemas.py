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



def _normalize_date(v: str) -> str:
    """Normalize date string to YYYY-MM-DD from multiple input formats."""
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError("Date must be in YYYY-MM-DD or DD-MM-YYYY format")


class SlotCreate(BaseModel):
    doctor_id: str
    date: str
    time: str
    duration_minutes: int = 15

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        return _normalize_date(v)



class BulkSlotCreate(BaseModel):
    """Schema for generating 15-min slots across a date/time range."""
    doctor_id: str
    start_date: str        # YYYY-MM-DD
    end_date: str          # YYYY-MM-DD
    start_time: str        # HH:MM  e.g. "09:00"
    end_time: str          # HH:MM  e.g. "13:00"
    duration_minutes: int = 15

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_dates(cls, v):
        return _normalize_date(v)

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_times(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format")


class BulkSlotCancel(BaseModel):
    """Schema for cancelling/disabling slots by date and time period."""
    doctor_id: str
    date: str                         # YYYY-MM-DD
    period: str = "all"               # "all" | "morning" | "evening"

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        return _normalize_date(v)

    @field_validator("period")
    @classmethod
    def validate_period(cls, v):
        allowed = {"all", "morning", "evening"}
        if v.lower() not in allowed:
            raise ValueError(f"period must be one of {allowed}")
        return v.lower()


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




class DoctorInfo(BaseModel):
    id: str
    name: str
    department: Optional[str] = None
    specialization: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Appointment(BaseModel):
    id: str | uuid.UUID = Field(default_factory=lambda: str(uuid.uuid4()))

    patient: Patient
    doctor_id: Optional[str] = None # Linking to a doctor if needed
    doctor: Optional[DoctorInfo] = None
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
            return _normalize_date(v)
        except ValueError:
            raise ValueError("dob must be in ISO format YYYY-MM-DD or DD/MM/YYYY")

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

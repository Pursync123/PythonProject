"""
SQLAlchemy ORM models for the Appointment Booking System
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Date, Time, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.db.session import Base


class SlotStatus(str, enum.Enum):
    """Enum for appointment slot status"""
    AVAILABLE = "available"
    BOOKED = "booked"
    DISABLED = "disabled"
    CANCELLED = "cancelled"


class AppointmentStatus(str, enum.Enum):
    """Enum for appointment status"""
    BOOKED = "booked"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class ActionType(str, enum.Enum):
    """Enum for audit log actions"""
    BOOK = "BOOK"
    CANCEL = "CANCEL"
    VIEW = "VIEW"
    UPDATE = "UPDATE"


class Doctor(Base):
    """Doctor information model"""
    __tablename__ = "doctors"

    id = Column(String(20), primary_key=True, unique=True)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    department = Column(String(100), nullable=False, index=True)
    specialization = Column(String(255), nullable=False)
    experience = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    slots = relationship("AvailableSlot", back_populates="doctor", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Doctor {self.id} - {self.name}>"


class Patient(Base):
    """Patient information model"""
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    dob = Column(Date, nullable=False)
    insurance_provider = Column(String(255), nullable=True)
    insurance_id = Column(String(50), nullable=True)
    blood_group = Column(String(5), nullable=True)
    allergies = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.id} - {self.first_name} {self.last_name}>"


class AvailableSlot(Base):
    """Available appointment slots model"""
    __tablename__ = "available_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_id = Column(String(20), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=15, nullable=False)
    status = Column(String(20), default=SlotStatus.AVAILABLE.value, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    doctor = relationship("Doctor", back_populates="slots")
    appointment = relationship("Appointment", back_populates="slot", uselist=False)

    # Composite index for faster queries
    __table_args__ = (
        Index('idx_doctor_date_time', 'doctor_id', 'date', 'time'),
        Index('idx_status_date', 'status', 'date'),
    )

    def __repr__(self):
        return f"<AvailableSlot {self.id} - {self.doctor_id} @ {self.date} {self.time}>"


class Appointment(Base):
    """Appointment booking model"""
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    doctor_id = Column(String(20), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("available_slots.id", ondelete="SET NULL"), nullable=True, unique=True)
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), default=AppointmentStatus.BOOKED.value, nullable=False, index=True)
    requested_datetime = Column(DateTime, nullable=False, index=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    slot = relationship("AvailableSlot", back_populates="appointment")

    # Composite index for queries
    __table_args__ = (
        Index('idx_patient_status', 'patient_id', 'status'),
        Index('idx_doctor_status', 'doctor_id', 'status'),
        Index('idx_appointment_audit', 'id', 'created_at'),
    )

    def __repr__(self):
        return f"<Appointment {self.id} - Patient {self.patient_id} with Doctor {self.doctor_id}>"


class AuditLog(Base):
    """Audit trail for all operations"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String(20), nullable=False, index=True)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="SET NULL"), nullable=True)
    doctor_id = Column(String(20), ForeignKey("doctors.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(String(255), nullable=True)  # Can be patient ID or admin ID
    details = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)  # Support IPv4 and IPv6
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), default="SUCCESS", nullable=False)  # SUCCESS or FAILURE
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Composite index for audit queries
    __table_args__ = (
        Index('idx_action_timestamp', 'action', 'created_at'),
        Index('idx_appointment_audit', 'appointment_id', 'created_at'),
    )

    def __repr__(self):
        return f"<AuditLog {self.id} - {self.action} @ {self.created_at}>"


class Department(Base):
    """Medical departments"""
    __tablename__ = "departments"

    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Department {self.id} - {self.name}>"


class ArchivedAvailableSlot(Base):
    """Archived appointment slots model"""
    __tablename__ = "archived_available_slots"

    id = Column(UUID(as_uuid=True), primary_key=True)
    doctor_id = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    archived_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<ArchivedAvailableSlot {self.id} - {self.doctor_id} @ {self.date} {self.time}>"


class ArchivedAppointment(Base):
    """Archived appointment booking model"""
    __tablename__ = "archived_appointments"

    id = Column(UUID(as_uuid=True), primary_key=True)
    patient_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    doctor_id = Column(String(20), nullable=False, index=True)
    slot_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    reason = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, index=True)
    requested_datetime = Column(DateTime, nullable=False, index=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    archived_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self):
        return f"<ArchivedAppointment {self.id} - Patient {self.patient_id}>"


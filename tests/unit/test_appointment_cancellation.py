import pytest
from unittest.mock import MagicMock, patch
import uuid
from datetime import datetime

from app.services.appointment_service import AppointmentService
from app.exceptions.custom import AppointmentNotFoundException

def test_cancel_appointment_sends_sms():
    # Setup
    db_session = MagicMock()
    service = AppointmentService(db=db_session)
    
    # Mock repositories
    service.appointment_repo = MagicMock()
    service.patient_repo = MagicMock()
    service.doctor_repo = MagicMock()
    service.slot_repo = MagicMock()
    
    appointment_id = str(uuid.uuid4())
    appt_uuid = uuid.UUID(appointment_id)
    
    # Mock models
    appt = MagicMock()
    appt.id = appt_uuid
    appt.patient_id = uuid.uuid4()
    appt.doctor_id = "doc001"
    appt.requested_datetime = datetime(2026, 7, 12, 10, 0, 0)
    appt.status = "booked"
    appt.slot_id = uuid.uuid4()
    
    patient = MagicMock()
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.phone = "+919876543210"
    
    doctor = MagicMock()
    doctor.name = "Jane Smith"
    
    service.appointment_repo.get_by_id.return_value = appt
    service.patient_repo.get_by_id.return_value = patient
    service.doctor_repo.get_by_id.return_value = doctor
    
    # Patch sms_service
    with patch("app.services.sms_service.sms_service") as mock_sms_service:
        # Execute
        result = service.cancel_appointment(appointment_id)
        
        # Verify
        assert result == {"status": "cancelled", "appointment_id": appointment_id}
        service.appointment_repo.cancel.assert_called_once_with(appt_uuid)
        service.slot_repo.update_status.assert_called_once_with(appt.slot_id, "available")
        service.patient_repo.get_by_id.assert_called_once_with(appt.patient_id)
        service.doctor_repo.get_by_id.assert_called_once_with(appt.doctor_id)
        
        mock_sms_service.send_appointment_cancellation.assert_called_once_with(
            patient_name="John Doe",
            patient_phone="+919876543210",
            doctor_name="Jane Smith",
            requested_datetime=appt.requested_datetime
        )

def test_cancel_appointment_already_cancelled():
    # Setup
    db_session = MagicMock()
    service = AppointmentService(db=db_session)
    
    service.appointment_repo = MagicMock()
    service.patient_repo = MagicMock()
    service.doctor_repo = MagicMock()
    
    appointment_id = str(uuid.uuid4())
    appt_uuid = uuid.UUID(appointment_id)
    
    appt = MagicMock()
    appt.status = "cancelled"
    
    service.appointment_repo.get_by_id.return_value = appt
    
    with patch("app.services.sms_service.sms_service") as mock_sms_service:
        result = service.cancel_appointment(appointment_id)
        
        assert result == {"status": "already_cancelled"}
        service.appointment_repo.cancel.assert_not_called()
        mock_sms_service.send_appointment_cancellation.assert_not_called()

def test_cancel_appointment_not_found():
    # Setup
    db_session = MagicMock()
    service = AppointmentService(db=db_session)
    
    service.appointment_repo = MagicMock()
    service.appointment_repo.get_by_id.return_value = None
    
    appointment_id = str(uuid.uuid4())
    
    with pytest.raises(AppointmentNotFoundException):
        service.cancel_appointment(appointment_id)

def test_cancel_appointment_sms_failure_does_not_block_cancellation():
    # Setup
    db_session = MagicMock()
    service = AppointmentService(db=db_session)
    
    # Mock repositories
    service.appointment_repo = MagicMock()
    service.patient_repo = MagicMock()
    service.doctor_repo = MagicMock()
    service.slot_repo = MagicMock()
    
    appointment_id = str(uuid.uuid4())
    appt_uuid = uuid.UUID(appointment_id)
    
    # Mock models
    appt = MagicMock()
    appt.id = appt_uuid
    appt.patient_id = uuid.uuid4()
    appt.doctor_id = "doc001"
    appt.requested_datetime = datetime(2026, 7, 12, 10, 0, 0)
    appt.status = "booked"
    appt.slot_id = uuid.uuid4()
    
    patient = MagicMock()
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.phone = "+919876543210"
    
    doctor = MagicMock()
    doctor.name = "Jane Smith"
    
    service.appointment_repo.get_by_id.return_value = appt
    service.patient_repo.get_by_id.return_value = patient
    service.doctor_repo.get_by_id.return_value = doctor
    
    # Patch sms_service to raise exception
    with patch("app.services.sms_service.sms_service") as mock_sms_service:
        mock_sms_service.send_appointment_cancellation.side_effect = Exception("SMS service error")
        
        # Execute (should succeed despite SMS failure)
        result = service.cancel_appointment(appointment_id)
        
        # Verify
        assert result == {"status": "cancelled", "appointment_id": appointment_id}
        service.appointment_repo.cancel.assert_called_once_with(appt_uuid)


def test_cancel_appointment_custom_slot_status():
    # Setup
    db_session = MagicMock()
    service = AppointmentService(db=db_session)
    
    # Mock repositories
    service.appointment_repo = MagicMock()
    service.patient_repo = MagicMock()
    service.doctor_repo = MagicMock()
    service.slot_repo = MagicMock()
    
    appointment_id = str(uuid.uuid4())
    appt_uuid = uuid.UUID(appointment_id)
    
    # Mock models
    appt = MagicMock()
    appt.id = appt_uuid
    appt.patient_id = uuid.uuid4()
    appt.doctor_id = "doc001"
    appt.requested_datetime = datetime(2026, 7, 12, 10, 0, 0)
    appt.status = "booked"
    appt.slot_id = uuid.uuid4()
    
    patient = MagicMock()
    patient.first_name = "John"
    patient.last_name = "Doe"
    patient.phone = "+919876543210"
    
    doctor = MagicMock()
    doctor.name = "Jane Smith"
    
    service.appointment_repo.get_by_id.return_value = appt
    service.patient_repo.get_by_id.return_value = patient
    service.doctor_repo.get_by_id.return_value = doctor
    
    with patch("app.services.sms_service.sms_service") as mock_sms_service:
        # Execute
        result = service.cancel_appointment(appointment_id, new_slot_status="disabled")
        
        # Verify slot_repo updated with "disabled"
        assert result == {"status": "cancelled", "appointment_id": appointment_id}
        service.appointment_repo.cancel.assert_called_once_with(appt_uuid)
        service.slot_repo.update_status.assert_called_once_with(appt.slot_id, "disabled")


def test_doctor_service_disable_available_slot():
    from app.services.doctor_service import DoctorService
    db_session = MagicMock()
    service = DoctorService(db=db_session)
    service.slot_repo = MagicMock()
    
    slot_id = str(uuid.uuid4())
    slot_uuid = uuid.UUID(slot_id)
    
    # Mock slot query to return a slot with no appointment
    mock_slot = MagicMock()
    mock_slot.appointment = None
    
    db_session.query.return_value.filter.return_value.first.return_value = mock_slot
    
    service.update_slot_status(slot_id, "disabled")
    
    service.slot_repo.update_status.assert_called_once_with(slot_uuid, "disabled")


def test_doctor_service_disable_booked_slot():
    from app.services.doctor_service import DoctorService
    db_session = MagicMock()
    service = DoctorService(db=db_session)
    service.slot_repo = MagicMock()
    
    slot_id = str(uuid.uuid4())
    slot_uuid = uuid.UUID(slot_id)
    
    # Mock slot and appointment
    mock_slot = MagicMock()
    mock_slot.id = slot_uuid
    
    mock_appt = MagicMock()
    mock_appt.id = uuid.uuid4()
    mock_appt.status = "booked"
    
    mock_slot.appointment = mock_appt
    
    # Setup query mock chain
    db_session.query.return_value.filter.return_value.first.return_value = mock_slot
    
    # Patch AppointmentService
    with patch("app.services.appointment_service.AppointmentService") as mock_appt_service_class:
        mock_appt_service_instance = mock_appt_service_class.return_value
        
        # Execute
        result = service.update_slot_status(slot_id, "disabled")
        
        # Verify AppointmentService cancel_appointment is called with Str ID and slot status "disabled"
        mock_appt_service_instance.cancel_appointment.assert_called_once_with(str(mock_appt.id), new_slot_status="disabled")
        db_session.refresh.assert_called_once_with(mock_slot)
        assert result == mock_slot


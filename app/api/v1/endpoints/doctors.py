from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.services.doctor_service import DoctorService
from app.schemas.schemas import (
    Doctor as DoctorSchema, SlotCreate, SlotUpdate,
    BulkSlotCreate, BulkSlotCancel,
    DoctorListResponse, DoctorResponse,
)

router = APIRouter()

@router.get("/doctors", response_model=DoctorListResponse)
def get_doctors(
    include_slots: bool = False,
    slot_limit: int = 5,
    specialization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all doctors with optional slot inclusion and specialization filtering."""
    service = DoctorService(db)
    doctors_data = service.get_all_active_doctors(
        include_slots=include_slots, 
        slot_limit=slot_limit,
        specialization=specialization
    )
    return {
        "status": "success",
        "count": len(doctors_data),
        "doctors": doctors_data
    }

@router.get("/doctors/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: str,
    include_slots: bool = True,
    slot_limit: int = 500,
    manage_mode: bool = False,
    db: Session = Depends(get_db)
):
    """Get specific doctor details and available slots."""
    service = DoctorService(db)
    doctor = service.get_doctor_by_id(doctor_id, include_slots=include_slots, slot_limit=slot_limit, manage_mode=manage_mode)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {
        "status": "success",
        "doctor": doctor
    }

@router.get("/available-slots")
def get_available_slots(
    department: Optional[str] = None,
    slot_limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get available slots by department."""
    service = DoctorService(db)
    result_doctors = service.get_available_slots(department, slot_limit=slot_limit)

    return {
        "status": "success",
        "filter_department": department,
        "total_doctors": len(result_doctors),
        "doctors": result_doctors
    }

@router.post("/doctors/{doctor_id}/slots")
def create_slot(
    doctor_id: str,
    slot_data: SlotCreate,
    db: Session = Depends(get_db)
):
    """Create a new available slot for a doctor."""
    if slot_data.doctor_id != doctor_id:
        raise HTTPException(status_code=400, detail="Doctor ID in path and body must match")
        
    service = DoctorService(db)
    new_slot = service.create_slot(slot_data)
    return {"status": "success", "slot": new_slot}

@router.post("/doctors/{doctor_id}/slots/bulk")
def create_bulk_slots(
    doctor_id: str,
    data: BulkSlotCreate,
    db: Session = Depends(get_db)
):
    """Generate multiple 15-min slots across a date/time range for a doctor."""
    if data.doctor_id != doctor_id:
        raise HTTPException(status_code=400, detail="Doctor ID in path and body must match")

    service = DoctorService(db)
    result = service.create_bulk_slots(data)
    return {"status": "success", **result}


@router.post("/doctors/{doctor_id}/slots/cancel")
def cancel_slots(
    doctor_id: str,
    data: BulkSlotCancel,
    db: Session = Depends(get_db)
):
    """Cancel/disable slots for a doctor on a given date and period (all/morning/evening)."""
    if data.doctor_id != doctor_id:
        raise HTTPException(status_code=400, detail="Doctor ID in path and body must match")

    service = DoctorService(db)
    result = service.cancel_slots(data)
    return {"status": "success", **result}


@router.patch("/slots/{slot_id}")
def update_slot_status(
    slot_id: str,
    status_update: SlotUpdate,
    db: Session = Depends(get_db)
):
    """Update the status of a slot (e.g., disable/enable)."""
    service = DoctorService(db)
    updated_slot = service.update_slot_status(slot_id, status_update.status)
    if not updated_slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    return {"status": "success", "slot": updated_slot}

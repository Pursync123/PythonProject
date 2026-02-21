from pydantic import BaseModel, ConfigDict
from typing import List

# Minimal Pydantic Model
class PatientSchema(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)

class AppointmentSchema(BaseModel):
    id: int
    patient: PatientSchema
    model_config = ConfigDict(from_attributes=True)

# Minimal ORM-like classes
class PatientORM:
    def __init__(self, name):
        self.name = name

class AppointmentORM:
    def __init__(self, id, patient):
        self.id = id
        self.patient = patient

def test_simple():
    print("--- Testing Simple Pydantic Config ---")
    
    pat_orm = PatientORM(name="John")
    appt_orm = AppointmentORM(id=1, patient=pat_orm)
    
    try:
        # direct validation
        valid_appt = AppointmentSchema.model_validate(appt_orm)
        print(f"✅ Success: {valid_appt}")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_simple()

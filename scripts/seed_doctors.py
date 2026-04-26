"""
Seed script to create database schema and persist doctors data into the new database.

Usage:
    python -m scripts.seed_doctors          # from project root
    python scripts/seed_doctors.py          # direct execution

This script will:
1. Create all tables if they don't exist (schema creation)
2. Seed departments
3. Seed doctors with realistic data
"""

import sys
import os
from datetime import datetime

# Add project root to sys.path so app modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import engine, SessionLocal, Base
from app.models.models import Doctor, Department


# ── Seed Data ─────────────────────────────────────────────────────────

DEPARTMENTS = [
    {"id": "cardiology",     "name": "Cardiology",     "description": "Heart and cardiovascular system specialists"},
    {"id": "dermatology",    "name": "Dermatology",    "description": "Skin, hair, and nail specialists"},
    {"id": "neurology",      "name": "Neurology",      "description": "Brain and nervous system specialists"},
    {"id": "orthopedics",    "name": "Orthopedics",    "description": "Bone, joint, and musculoskeletal specialists"},
    {"id": "pediatrics",     "name": "Pediatrics",     "description": "Medical care for infants, children, and adolescents"},
    {"id": "general",        "name": "General Medicine", "description": "Primary care and general health"},
    {"id": "ent",            "name": "ENT",            "description": "Ear, nose, and throat specialists"},
    {"id": "ophthalmology",  "name": "Ophthalmology",  "description": "Eye care and vision specialists"},
]

DOCTORS = [
    {
        "id": "DOC001",
        "name": "Dr. Sarah Johnson",
        "email": "sarah.johnson@hospital.com",
        "department": "cardiology",
        "specialization": "Interventional Cardiology",
        "experience": 15,
        "phone": "+1-555-0101",
        "bio": "Board-certified cardiologist with 15 years of experience in interventional cardiology and cardiac catheterization.",
        "is_active": True,
    },
    {
        "id": "DOC002",
        "name": "Dr. Michael Chen",
        "email": "michael.chen@hospital.com",
        "department": "neurology",
        "specialization": "Neurophysiology",
        "experience": 12,
        "phone": "+1-555-0102",
        "bio": "Specialist in neurophysiology and movement disorders with extensive research in Parkinson's disease.",
        "is_active": True,
    },
    {
        "id": "DOC003",
        "name": "Dr. Emily Williams",
        "email": "emily.williams@hospital.com",
        "department": "pediatrics",
        "specialization": "Pediatric Oncology",
        "experience": 10,
        "phone": "+1-555-0103",
        "bio": "Dedicated pediatric oncologist focused on childhood leukemia and innovative treatment approaches.",
        "is_active": True,
    },
    {
        "id": "DOC004",
        "name": "Dr. Raj Patel",
        "email": "raj.patel@hospital.com",
        "department": "orthopedics",
        "specialization": "Sports Medicine & Joint Replacement",
        "experience": 18,
        "phone": "+1-555-0104",
        "bio": "Renowned orthopedic surgeon specializing in minimally invasive joint replacement and sports injuries.",
        "is_active": True,
    },
    {
        "id": "DOC005",
        "name": "Dr. Lisa Anderson",
        "email": "lisa.anderson@hospital.com",
        "department": "dermatology",
        "specialization": "Cosmetic Dermatology",
        "experience": 8,
        "phone": "+1-555-0105",
        "bio": "Expert in cosmetic dermatology, laser treatments, and skin cancer screening.",
        "is_active": True,
    },
    {
        "id": "DOC006",
        "name": "Dr. James Wilson",
        "email": "james.wilson@hospital.com",
        "department": "general",
        "specialization": "Internal Medicine",
        "experience": 20,
        "phone": "+1-555-0106",
        "bio": "Seasoned internist with two decades of experience in preventive medicine and chronic disease management.",
        "is_active": True,
    },
    {
        "id": "DOC007",
        "name": "Dr. Priya Sharma",
        "email": "priya.sharma@hospital.com",
        "department": "ent",
        "specialization": "Otolaryngology",
        "experience": 11,
        "phone": "+1-555-0107",
        "bio": "ENT specialist experienced in sinus surgery, hearing disorders, and pediatric ENT conditions.",
        "is_active": True,
    },
    {
        "id": "DOC008",
        "name": "Dr. David Kim",
        "email": "david.kim@hospital.com",
        "department": "ophthalmology",
        "specialization": "Retinal Surgery",
        "experience": 14,
        "phone": "+1-555-0108",
        "bio": "Expert ophthalmologist specializing in retinal surgery, LASIK, and diabetic eye disease.",
        "is_active": True,
    },
]


# ── Helper Functions ──────────────────────────────────────────────────

def create_schema():
    """Create all database tables based on SQLAlchemy models."""
    print("Creating database schema (tables)...")
    Base.metadata.create_all(bind=engine)
    print("[OK] Schema created successfully.\n")


def seed_departments(db):
    """Insert or update departments."""
    print("Seeding departments...")
    created = 0
    updated = 0

    for dept_data in DEPARTMENTS:
        # Check by id first, then by name (name has unique constraint)
        existing = db.query(Department).filter(Department.id == dept_data["id"]).first()
        if not existing:
            existing = db.query(Department).filter(Department.name == dept_data["name"]).first()
        
        if existing:
            existing.name = dept_data["name"]
            existing.description = dept_data["description"]
            existing.is_active = True
            updated += 1
        else:
            dept = Department(
                id=dept_data["id"],
                name=dept_data["name"],
                description=dept_data["description"],
                is_active=True,
                created_at=datetime.utcnow(),
            )
            db.add(dept)
            created += 1

    db.commit()
    print(f"[OK] Departments - {created} created, {updated} updated.\n")


def seed_doctors(db):
    """Insert or update doctors."""
    print("Seeding doctors...")
    created = 0
    updated = 0

    for doc_data in DOCTORS:
        existing = db.query(Doctor).filter(Doctor.id == doc_data["id"]).first()
        if existing:
            existing.name = doc_data["name"]
            existing.email = doc_data["email"]
            existing.department = doc_data["department"]
            existing.specialization = doc_data["specialization"]
            existing.experience = doc_data["experience"]
            existing.phone = doc_data["phone"]
            existing.bio = doc_data["bio"]
            existing.is_active = doc_data["is_active"]
            existing.updated_at = datetime.utcnow()
            updated += 1
        else:
            doctor = Doctor(
                id=doc_data["id"],
                name=doc_data["name"],
                email=doc_data["email"],
                department=doc_data["department"],
                specialization=doc_data["specialization"],
                experience=doc_data["experience"],
                phone=doc_data["phone"],
                bio=doc_data["bio"],
                is_active=doc_data["is_active"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(doctor)
            created += 1

    db.commit()
    print(f"[OK] Doctors - {created} created, {updated} updated.\n")


def verify_data(db):
    """Verify seeded data by querying it back."""
    print("Verifying seeded data...")
    
    dept_count = db.query(Department).count()
    doc_count = db.query(Doctor).filter(Doctor.is_active == True).count()
    
    print(f"  Departments in DB : {dept_count}")
    print(f"  Active doctors    : {doc_count}")
    print()

    doctors = db.query(Doctor).filter(Doctor.is_active == True).order_by(Doctor.id).all()
    print(f"  {'ID':<10} {'Name':<25} {'Department':<18} {'Specialization':<35} {'Exp'}")
    print(f"  {'-'*10} {'-'*25} {'-'*18} {'-'*35} {'-'*4}")
    for doc in doctors:
        print(f"  {doc.id:<10} {doc.name:<25} {doc.department:<18} {doc.specialization:<35} {doc.experience}y")
    
    print("\n[OK] Verification complete.")


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  AI Receptionist - Database Seed Script")
    print("=" * 60)
    print()

    # Step 1: Create schema
    create_schema()

    # Step 2: Seed data
    db = SessionLocal()
    try:
        seed_departments(db)
        seed_doctors(db)
        verify_data(db)
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()

    print()
    print("=" * 60)
    print("  Seeding completed successfully!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

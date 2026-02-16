import sys
import os
from datetime import datetime, date, time, timedelta

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.models import Doctor, AvailableSlot, SlotStatus

def seed_future_slots():
    db = SessionLocal()
    try:
        doctors = db.query(Doctor).filter(Doctor.is_active == True).all()
        if not doctors:
            print("No active doctors found.")
            return

        start_date = date.today()
        end_date = start_date + timedelta(days=5)
        
        print(f"Seeding slots from {start_date} to {end_date}...")
        
        slots_to_add = []
        for doc in doctors:
            current_date = start_date
            while current_date <= end_date:
                # 9:00 AM to 5:00 PM (17:00) every 15 minutes
                start_time = time(9, 0)
                end_time = time(17, 0)
                curr_time = datetime.combine(date.today(), start_time)
                end_datetime = datetime.combine(date.today(), end_time)
                
                while curr_time < end_datetime:
                    slot_time = curr_time.time()
                    
                    # Check if slot already exists
                    exists = db.query(AvailableSlot).filter(
                        AvailableSlot.doctor_id == doc.id,
                        AvailableSlot.date == current_date,
                        AvailableSlot.time == slot_time
                    ).first()
                    
                    if not exists:
                        slot = AvailableSlot(
                            doctor_id=doc.id,
                            date=current_date,
                            time=slot_time,
                            duration_minutes=15,
                            status=SlotStatus.AVAILABLE.value
                        )
                        db.add(slot)
                        slots_to_add.append(slot)
                        print(f"Added slot for {doc.name}: {current_date} {slot_time}", end='\r')
                    
                    curr_time += timedelta(minutes=15)
                
                current_date += timedelta(days=1)
            print(f"Finished processing {doc.name}")

        
        db.commit()
        print(f"Successfully added {len(slots_to_add)} new slots across {len(doctors)} doctors.")
    
    except Exception as e:
        db.rollback()
        print(f"Error seeding slots: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_future_slots()

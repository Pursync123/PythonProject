import sys
import os
from datetime import date

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.models import AvailableSlot

db = SessionLocal()
try:
    today = date.today()
    slots = db.query(AvailableSlot).filter(AvailableSlot.date >= today).order_by(AvailableSlot.date, AvailableSlot.time).all()
    print(f"Found {len(slots)} slots from today onwards.")
    if slots:
        dates = sorted(list(set(s.date for s in slots)))
        print(f"Dates with slots: {dates}")
        for d in dates:
            day_slots = [s for s in slots if s.date == d]
            print(f"  {d}: {len(day_slots)} slots")
            times = sorted(list(set(s.time for s in day_slots)))
            print(f"    Times: {times}")
finally:
    db.close()

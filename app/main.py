from fastapi import FastAPI
import logging
from app.api.v1.api import api_router
from app.exceptions.handlers import add_exception_handlers
from app.core.config import settings

from contextlib import asynccontextmanager
from app.core.scheduler import start_scheduler, stop_scheduler

# Configure logging for deployment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Clean up duplicate slots in the DB to fix "still showing available" bug
    try:
        from app.db.session import SessionLocal
        from app.models.models import AvailableSlot
        db = SessionLocal()
        slots = db.query(AvailableSlot).all()
        seen = {}
        for s in slots:
            key = (s.doctor_id, s.date, s.time)
            if key not in seen:
                seen[key] = s
            else:
                existing = seen[key]
                # Prioritize keeping booked slots over available duplicates
                if s.status != 'available' and existing.status == 'available':
                    db.delete(existing)
                    seen[key] = s
                elif s.status == 'available' and existing.status != 'available':
                    db.delete(s)
                else:
                    db.delete(s)
        db.commit()
        db.close()
        logger.info("Successfully cleaned up duplicate database slots")
    except Exception as e:
        logger.error(f"Failed to clean up slots: {e}")

    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(title=settings.PROJECT_NAME, version="1.1.0", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

# Set all CORS enabled origins before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

add_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to AI Receptionist API. Visit /docs for documentation."}



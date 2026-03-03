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
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(title=settings.PROJECT_NAME, version="1.1.0", lifespan=lifespan)

add_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to AI Receptionist API. Visit /docs for documentation."}

from fastapi.middleware.cors import CORSMiddleware

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

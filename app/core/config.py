import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Determine project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Appointment Booking API"
    API_V1_STR: str = "/api/v1"
    
    # Database
    # DATABASE_URL: str = "postgresql://ranga:lQHuZjjAtYduMoYuAL6FSHTsBd75u3Qd@dpg-d58jgkogjchc73a744k0-a.virginia-postgres.render.com/ai_receptionist_3gp5?sslmode=require"
    DATABASE_URL: str = "postgresql://ranga:04ZD9k3P7DJhl0IWjVofErqi2cuSMFbU@dpg-d6pgod15pdvs73a7r6t0-a.oregon-postgres.render.com/ai_receptionist_ndru?sslmode=require"
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

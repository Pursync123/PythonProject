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
    DATABASE_URL: str = "postgresql://ranga:cOPVW69EF3RtZPKGI80AWjaZuIJ1Blpo@dpg-d7mudo0k1i2s739bobl0-a.oregon-postgres.render.com/ai_receptionist_ndru_sod8?sslmode=require"
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

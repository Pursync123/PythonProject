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
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None
    TWILIO_WHATSAPP_FROM_NUMBER: Optional[str] = None
    TWILIO_WHATSAPP_CONTENT_SID: Optional[str] = None

    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

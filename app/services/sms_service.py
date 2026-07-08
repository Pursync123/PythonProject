import logging
from typing import Optional
from datetime import datetime
from twilio.rest import Client
from app.core.config import settings

logger = logging.getLogger(__name__)

class SmsService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_FROM_NUMBER
        
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")

    def format_phone_number(self, phone: str) -> str:
        """Format phone number to E.164 format, forcing +91 for Indian users"""
        if not phone:
            return ""
        # Keep only digits
        digits = "".join(c for c in phone if c.isdigit())
        
        # Indian mobile numbers are 10 digits.
        # If the number has at least 10 digits, extract the last 10 digits and prepend +91.
        if len(digits) >= 10:
            return f"+91{digits[-10:]}"
        
        # Fallback for short numbers
        return f"+91{digits}"

    def send_sms(self, to_number: str, body: str) -> Optional[str]:
        """Send a basic SMS via Twilio"""
        if not self.client:
            logger.warning("Twilio client is not initialized. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
            return None
        
        if not self.from_number:
            logger.warning("TWILIO_FROM_NUMBER is not set. Cannot send SMS.")
            return None

        formatted_to = self.format_phone_number(to_number)
        try:
            logger.info(f"Sending SMS to {formatted_to} from {self.from_number}")
            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=formatted_to
            )
            logger.info(f"SMS successfully sent: SID={message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Error sending Twilio SMS to {formatted_to}: {e}", exc_info=True)
            return None

    def send_appointment_confirmation(
        self, 
        patient_name: str, 
        patient_phone: str, 
        doctor_name: str, 
        requested_datetime: datetime
    ) -> Optional[str]:
        """Send appointment confirmation SMS to patient"""
        if not patient_phone:
            logger.warning("No phone number provided for patient. Skipping SMS.")
            return None

        # Format datetime nicely
        try:
            # e.g., "Wednesday, July 08, 2026 at 09:00 AM"
            formatted_time = requested_datetime.strftime("%A, %B %d, %Y at %I:%M %p")
        except Exception:
            formatted_time = str(requested_datetime)

        body = (
            f"Hello {patient_name}, your appointment with Dr. {doctor_name} "
            f"has been successfully booked for {formatted_time}. "
            f"Thank you!"
        )
        return self.send_sms(patient_phone, body)

sms_service = SmsService()

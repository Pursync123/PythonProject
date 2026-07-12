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

    def send_whatsapp_message(
        self,
        to_number: str,
        content_sid: Optional[str] = None,
        content_variables: Optional[str] = None,
        body: Optional[str] = None
    ) -> Optional[str]:
        """Send a WhatsApp message via Twilio (either using templates or freeform body)"""
        if not self.client:
            logger.warning("Twilio client is not initialized. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN.")
            return None

        formatted_to = self.format_phone_number(to_number)
        if not formatted_to.startswith("whatsapp:"):
            whatsapp_to = f"whatsapp:{formatted_to}"
        else:
            whatsapp_to = formatted_to

        whatsapp_from = getattr(settings, "TWILIO_WHATSAPP_FROM_NUMBER", "whatsapp:+14155238886") or "whatsapp:+14155238886"

        try:
            params = {
                "from_": whatsapp_from,
                "to": whatsapp_to
            }
            if content_sid:
                params["content_sid"] = content_sid
                if content_variables:
                    params["content_variables"] = content_variables
                logger.info(f"Sending WhatsApp via template {content_sid} to {whatsapp_to} from {whatsapp_from}")
            elif body:
                params["body"] = body
                logger.info(f"Sending freeform WhatsApp message to {whatsapp_to} from {whatsapp_from}")
            else:
                logger.error("Must provide either content_sid or body to send a WhatsApp message.")
                return None

            message = self.client.messages.create(**params)
            logger.info(f"WhatsApp successfully sent: SID={message.sid}")
            return message.sid
        except Exception as e:
            logger.error(f"Error sending Twilio WhatsApp to {whatsapp_to}: {e}", exc_info=True)
            return None

    def send_appointment_confirmation(
        self, 
        patient_name: str, 
        patient_phone: str, 
        doctor_name: str, 
        requested_datetime: datetime
    ) -> Optional[str]:
        """Send appointment confirmation SMS and WhatsApp to patient"""
        if not patient_phone:
            logger.warning("No phone number provided for patient. Skipping messages.")
            return None

        # Convert string to datetime if necessary to prevent errors
        if isinstance(requested_datetime, str):
            try:
                requested_datetime = datetime.fromisoformat(requested_datetime.replace("Z", "+00:00"))
            except Exception:
                try:
                    requested_datetime = datetime.strptime(requested_datetime, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    logger.error(f"Failed to parse requested_datetime string: {requested_datetime}")

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
        sms_sid = self.send_sms(patient_phone, body)

        # Send WhatsApp confirmation
        try:
            # 1. Try sending the custom freeform message body first (works if inside 24-hour window)
            logger.info("Attempting to send custom freeform WhatsApp message...")
            result_sid = self.send_whatsapp_message(
                to_number=patient_phone,
                body=body
            )
            
            # 2. If it fails or returns None, fallback to the pre-approved Sandbox template
            if not result_sid:
                logger.info("Freeform WhatsApp message failed (possibly outside 24-hour session). Falling back to template...")
                date_str = f"{requested_datetime.day}/{requested_datetime.month}"
                
                # Format time nicely: "3pm" or "3:30pm"
                time_str = requested_datetime.strftime("%I:%M %p").lower().strip().replace(" ", "")
                if time_str.startswith("0"):
                    time_str = time_str[1:]
                if time_str.endswith(":00am"):
                    time_str = time_str.replace(":00am", "am")
                elif time_str.endswith(":00pm"):
                    time_str = time_str.replace(":00pm", "pm")
                    
                import json
                content_vars = json.dumps({"1": date_str, "2": time_str})
                content_sid = getattr(settings, "TWILIO_WHATSAPP_CONTENT_SID", "HXb5b62575e6e4ff6129ad7c8efe1f983e") or "HXb5b62575e6e4ff6129ad7c8efe1f983e"
                
                self.send_whatsapp_message(
                    to_number=patient_phone,
                    content_sid=content_sid,
                    content_variables=content_vars
                )
        except Exception as whatsapp_err:
            logger.error(f"Failed to send WhatsApp confirmation: {whatsapp_err}", exc_info=True)

        return sms_sid

sms_service = SmsService()

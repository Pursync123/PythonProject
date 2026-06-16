# Rainbow Maternity Clinic - Appointment Booking System

## Project Documentation

---

## 1. Project Overview

A **FastAPI-based REST API** for an AI-powered medical appointment booking system, integrated with **Retell AI** for voice-based interactions.

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Database | PostgreSQL (Render) |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| AI Integration | Retell AI |
| Hosting | Render |

### Database Connection Details

| Property | Value |
|----------|-------|
| Hostname | `dpg-d58jgkogjchc73a744k0-a.virginia-postgres.render.com` |
| Port | `5432` |
| Database | `ai_receptionist_3gp5` |
| Username | `ranga` |
| External URL | `postgresql://ranga:lQHuZjjAtYduMoYuAL6FSHTsBd75u3Qd@dpg-d58jgkogjchc73a744k0-a.virginia-postgres.render.com/ai_receptionist_3gp5` |

---

## 2. Architecture

### End-to-End Flow

```mermaid
sequenceDiagram
    participant User as 👤 Caller
    participant Retell as 🤖 Retell AI
    participant API as 🖥️ FastAPI
    participant DB as 🗄️ PostgreSQL

    User->>Retell: "Book appointment for Siva"
    Retell->>API: POST /api/v1/book-appointment
    API->>API: Unwrap "args" & Validate
    API->>DB: Check slot availability
    API->>DB: Create Patient + Appointment
    API-->>Retell: {"status": "booked", ...}
    Retell->>User: "Appointment confirmed!"
```

### System Components

```mermaid
graph TB
    subgraph API["FastAPI Backend"]
        Endpoints["📍 Endpoints"]
        Schemas["📋 Pydantic Schemas"]
        Services["⚙️ Services"]
        Repos["📦 Repositories"]
    end
    
    subgraph DB["PostgreSQL"]
        Doctors["👨‍⚕️ Doctors"]
        Patients["👤 Patients"]
        Slots["📅 Slots"]
        Appointments["📝 Appointments"]
        AuditLogs["📜 Audit Logs"]
    end
    
    Endpoints --> Schemas --> Services --> Repos --> DB
```

---

## 3. Project Structure

```
PythonProject/
├── main.py                    # Entry point (uvicorn)
├── app/
│   ├── main.py               # FastAPI app initialization
│   ├── core/
│   │   └── config.py         # Settings (DATABASE_URL, etc.)
│   ├── db/
│   │   └── session.py        # SQLAlchemy engine & session
│   ├── models/
│   │   └── models.py         # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── api/v1/
│   │   ├── api.py            # Router aggregation
│   │   └── endpoints/
│   │       ├── appointments.py
│   │       ├── doctors.py
│   │       └── patients.py
│   ├── services/
│   │   ├── appointment_service.py
│   │   ├── doctor_service.py
│   │   └── patient_service.py
│   ├── repositories/
│   │   ├── appointment.py
│   │   ├── available_slot.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   └── audit_log.py
│   └── exceptions/
│       ├── custom.py         # Domain exceptions
│       └── handlers.py       # Global exception handlers
├── alembic/                  # Database migrations
├── scripts/                  # Utility scripts
└── pyproject.toml           # Dependencies
```

---

## 4. Database Models

### Entity Relationship Diagram

```mermaid
erDiagram
    DOCTORS ||--o{ AVAILABLE_SLOTS : has
    DOCTORS ||--o{ APPOINTMENTS : treats
    PATIENTS ||--o{ APPOINTMENTS : books
    AVAILABLE_SLOTS ||--o| APPOINTMENTS : fulfills
    APPOINTMENTS ||--o{ AUDIT_LOGS : generates

    DOCTORS {
        string id PK "DOC001"
        string name
        string department
        string specialization
        int experience
        bool is_active
    }

    PATIENTS {
        uuid id PK
        string first_name
        string last_name
        date dob
        string insurance_provider
    }

    AVAILABLE_SLOTS {
        uuid id PK
        string doctor_id FK
        date date
        time time
        int duration_minutes
        string status "available|booked"
    }

    APPOINTMENTS {
        uuid id PK
        uuid patient_id FK
        string doctor_id FK
        uuid slot_id FK
        text reason
        datetime requested_datetime
        string status "booked|cancelled"
    }

    AUDIT_LOGS {
        uuid id PK
        string action "BOOK|CANCEL"
        uuid appointment_id FK
        text details
        datetime created_at
    }
```

### Model Details

| Model | Table | Key Fields |
|-------|-------|------------|
| `Doctor` | `doctors` | `id`, `name`, `department`, `specialization`, `experience` |
| `Patient` | `patients` | `id`, `first_name`, `last_name`, `dob`, `insurance_provider` |
| `AvailableSlot` | `available_slots` | `id`, `doctor_id`, `date`, `time`, `status` |
| `Appointment` | `appointments` | `id`, `patient_id`, `doctor_id`, `slot_id`, `reason`, `status` |
| `AuditLog` | `audit_logs` | `id`, `action`, `appointment_id`, `details` |

---

## 5. API Endpoints

### Base URL: `/api/v1`

### Appointments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/book-appointment` | Book a new appointment |
| `POST` | `/cancel-appointment` | Cancel an existing appointment |
| `GET` | `/appointments` | List all booked appointments |
| `GET` | `/appointments/{id}` | Get appointment by ID |

### Doctors

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/doctors` | List all doctors (with optional slots) |
| `GET` | `/doctors/{id}` | Get doctor details + available slots |
| `GET` | `/available-slots` | Get slots by department filter |

---

## 6. Pydantic Schemas

### AppointmentRequest (Input)

```python
class AppointmentRequest(BaseModel):
    doctor_id: Optional[str] = None
    first_name: str
    last_name: str
    dob: str                    # YYYY-MM-DD
    insurance_provider: str
    reason: str
    requested_datetime: str     # ISO 8601

    # Validators
    @field_validator("dob")      # Validates date format
    @field_validator("requested_datetime")  # Validates datetime
    @model_validator(mode='before')  # Unwraps Retell "args"
```

### JSON Schema (for Retell AI)

```json
{
  "type": "object",
  "required": ["first_name", "last_name", "dob", 
               "insurance_provider", "reason", "requested_datetime"],
  "properties": {
    "first_name": {"type": "string", "description": "Patient first name"},
    "last_name": {"type": "string", "description": "Patient last name"},
    "dob": {"type": "string", "description": "Date of birth (YYYY-MM-DD)"},
    "insurance_provider": {"type": "string", "description": "Insurance provider"},
    "reason": {"type": "string", "description": "Reason for visit"},
    "requested_datetime": {"type": "string", "description": "ISO 8601 datetime"},
    "doctor_id": {"type": "string", "description": "Optional doctor ID"}
  }
}
```

---

## 7. Service Layer Logic

### AppointmentService.book_appointment()

```mermaid
flowchart TD
    A[Receive Request] --> B{Is datetime in future?}
    B -->|No| C[Throw 400 Error]
    B -->|Yes| D{doctor_id provided?}
    D -->|Yes| E[Find slot for that doctor]
    D -->|No| F[Search all doctors for slot]
    E --> G{Slot found?}
    F --> G
    G -->|No| H[Throw 409 SlotUnavailable]
    G -->|Yes| I[Create Patient]
    I --> J[Update Slot to 'booked']
    J --> K[Create Appointment]
    K --> L[Return Success Response]
```

### Key Business Rules

1. **Past Date Validation** - Rejects appointments in the past
2. **Slot Availability** - Only books available slots
3. **Auto Patient Creation** - Creates patient record on each booking
4. **Atomic Transaction** - Slot update + appointment creation in one transaction

---

## 8. Exception Handling

### Custom Exceptions

| Exception | Status | Message |
|-----------|--------|---------|
| `AppError` | 400 | Base application error |
| `SlotUnavailableException` | 409 | "That slot is no longer available..." |
| `AppointmentNotFoundException` | 404 | "Appointment not found" |
| `PatientNotFoundException` | 404 | "Patient not found" |

### Validation Error Handler

Converts Pydantic validation errors to conversational messages:
```
"I'm sorry, but I seem to be missing some information. The 'first_name' is missing."
```

---

## 9. Retell AI Integration

### Payload Handling

Retell sends data wrapped in `args`:
```json
{
  "args": {
    "first_name": "Siva",
    "last_name": "Reddy",
    ...
  },
  "name": "book-appointment"
}
```

The `model_validator` automatically unwraps this:
```python
@model_validator(mode='before')
def unwrap_retell_args(cls, data):
    if isinstance(data, dict) and "args" in data:
        return data["args"]
    return data
```

---

## 10. Running the Project

### Local Development

```bash
# Install dependencies
pip install -e .

# Run with hot-reload
python main.py
# Server runs at http://localhost:8000
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |

### Database Migrations

```bash
alembic upgrade head
```

### Background Jobs (Archiving)

To keep the active database small and fast, the project includes a script to move old appointments and available slots into archive tables.
You can run it manually:
```bash
python scripts/archive_old_records.py --days 15
```

**Recommended Setup:** Configure a Cron Job to run this automatically every night on your server:
```bash
# Open crontab: crontab -e
# Run daily at 2:00 AM
0 2 * * * cd /path/to/PythonProject && .venv/bin/python scripts/archive_old_records.py >> /var/log/appointment_archive.log 2>&1
```

---

## 11. Example API Calls

### Book Appointment

```bash
curl -X POST "http://localhost:8000/api/v1/book-appointment" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Siva",
    "last_name": "Reddy",
    "dob": "1987-06-10",
    "insurance_provider": "MediBuddy",
    "reason": "Pediatric care",
    "requested_datetime": "2026-01-20T09:30:00",
    "doctor_id": "DOC003"
  }'
```

### Response (Success)

```json
{
  "status": "booked",
  "appointment": {
    "id": "a1b2c3d4-...",
    "doctor_id": "DOC003",
    "patient": {
      "first_name": "Siva",
      "last_name": "Reddy"
    },
    "requested_datetime": "2026-01-20 09:30:00"
  }
}
```

### Get Available Doctors

```bash
curl "http://localhost:8000/api/v1/doctors?include_slots=true&slot_limit=5"
```

---

## 12. Deployment (Render)

1. Push code to GitHub
2. Render auto-deploys from `code_optimization` branch
3. Uses `Dockerfile` for containerization
4. PostgreSQL database hosted on Render

---

*Documentation generated on 2026-01-17*

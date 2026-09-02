-- ========================================
-- AI Receptionist Appointment Booking System
-- PostgreSQL Schema
-- Database: ai_receptionist_3gp5
-- ========================================

-- ========================================
-- 1. ENUMS (Custom Types)
-- ========================================

CREATE TYPE slot_status AS ENUM ('available', 'booked', 'cancelled');
CREATE TYPE appointment_status AS ENUM ('booked', 'cancelled', 'completed', 'no_show', 'pending');
CREATE TYPE action_type AS ENUM ('CREATE', 'READ', 'UPDATE', 'DELETE', 'BOOK', 'CANCEL');

-- ========================================
-- 2. DEPARTMENTS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_active ON departments(is_active);
CREATE INDEX idx_departments_name ON departments(name);

-- ========================================
-- 3. DOCTORS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS doctors (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(100) NOT NULL,
    specialization VARCHAR(255) NOT NULL,
    experience INTEGER NOT NULL CHECK (experience >= 0),
    bio TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_doctors_active ON doctors(is_active);
CREATE INDEX idx_doctors_department ON doctors(department);
CREATE INDEX idx_doctors_specialization ON doctors(specialization);
CREATE INDEX idx_doctors_email ON doctors(email);

-- ========================================
-- 4. PATIENTS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    dob DATE NOT NULL,
    gender VARCHAR(10),
    blood_group VARCHAR(5),
    insurance_provider VARCHAR(255),
    insurance_id VARCHAR(50),
    allergies TEXT,
    medical_history TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_email CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT valid_age CHECK (EXTRACT(YEAR FROM AGE(dob)) >= 0),
    CONSTRAINT valid_blood_group CHECK (blood_group IS NULL OR blood_group IN ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'))
);

CREATE INDEX idx_patients_active ON patients(is_active);
CREATE INDEX idx_patients_email ON patients(email);
CREATE INDEX idx_patients_phone ON patients(phone);
CREATE INDEX idx_patients_full_name ON patients(first_name, last_name);
CREATE INDEX idx_patients_dob ON patients(dob);

-- ========================================
-- 5. AVAILABLE SLOTS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS available_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    duration_minutes INTEGER NOT NULL DEFAULT 30,
    status slot_status DEFAULT 'available',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    CONSTRAINT valid_duration CHECK (duration_minutes > 0 AND duration_minutes <= 480),
    CONSTRAINT valid_time CHECK (time >= '07:00'::TIME AND time <= '22:00'::TIME),
    CONSTRAINT unique_slot UNIQUE (doctor_id, date, time)
);

CREATE INDEX idx_slots_doctor_date_time ON available_slots(doctor_id, date, time);
CREATE INDEX idx_slots_status_date ON available_slots(status, date);
CREATE INDEX idx_slots_doctor_status ON available_slots(doctor_id, status);
CREATE INDEX idx_slots_date_range ON available_slots(date) WHERE status = 'available';

-- ========================================
-- 6. APPOINTMENTS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL,
    doctor_id VARCHAR(20) NOT NULL,
    slot_id UUID,
    reason TEXT NOT NULL,
    notes TEXT,
    status appointment_status DEFAULT 'pending',
    requested_datetime TIMESTAMP NOT NULL,
    confirmed_datetime TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES available_slots(id) ON DELETE SET NULL,
    CONSTRAINT single_slot_booking UNIQUE (slot_id),
    CONSTRAINT valid_cancellation CHECK (
        (status != 'cancelled' AND cancelled_at IS NULL) OR
        (status = 'cancelled' AND cancelled_at IS NOT NULL)
    )
);

CREATE INDEX idx_appointments_patient_status ON appointments(patient_id, status);
CREATE INDEX idx_appointments_doctor_status ON appointments(doctor_id, status);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_appointments_datetime ON appointments(requested_datetime);
CREATE INDEX idx_appointments_created ON appointments(created_at);
CREATE INDEX idx_appointments_slot ON appointments(slot_id);

-- ========================================
-- 7. AUDIT LOGS TABLE
-- ========================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action action_type NOT NULL,
    appointment_id UUID,
    patient_id UUID,
    doctor_id VARCHAR(20),
    user_id VARCHAR(255),
    details TEXT NOT NULL,
    ip_address INET,
    user_agent VARCHAR(500),
    status VARCHAR(20) DEFAULT 'SUCCESS',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_action_timestamp ON audit_logs(action, created_at);
CREATE INDEX idx_audit_appointment ON audit_logs(appointment_id, created_at);
CREATE INDEX idx_audit_patient ON audit_logs(patient_id, created_at);
CREATE INDEX idx_audit_user ON audit_logs(user_id, created_at);
CREATE INDEX idx_audit_status ON audit_logs(status, created_at);

-- ========================================
-- 8. NOTIFICATIONS TABLE (Optional)
-- ========================================

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    appointment_id UUID NOT NULL,
    patient_id UUID NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_appointment ON notifications(appointment_id);
CREATE INDEX idx_notifications_patient ON notifications(patient_id);
CREATE INDEX idx_notifications_sent ON notifications(is_sent, created_at);

-- ========================================
-- 9. CANCELLATION POLICIES TABLE (Optional)
-- ========================================

CREATE TABLE IF NOT EXISTS cancellation_policies (
    id VARCHAR(50) PRIMARY KEY,
    doctor_id VARCHAR(20),
    hours_before_cancellation INTEGER DEFAULT 24,
    cancellation_fee DECIMAL(10, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

-- ========================================
-- 10. WORKING HOURS TABLE (Optional)
-- ========================================

CREATE TABLE IF NOT EXISTS doctor_working_hours (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doctor_id VARCHAR(20) NOT NULL,
    day_of_week INTEGER NOT NULL CHECK (day_of_week >= 0 AND day_of_week <= 6),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    CONSTRAINT valid_hours CHECK (start_time < end_time),
    CONSTRAINT unique_working_hours UNIQUE (doctor_id, day_of_week)
);

CREATE INDEX idx_working_hours_doctor ON doctor_working_hours(doctor_id);

-- ========================================
-- VIEWS
-- ========================================

-- View for upcoming available appointments
CREATE OR REPLACE VIEW upcoming_appointments AS
SELECT
    a.id,
    a.patient_id,
    p.first_name,
    p.last_name,
    p.email,
    a.doctor_id,
    d.name AS doctor_name,
    a.requested_datetime,
    a.status,
    a.reason
FROM appointments a
JOIN patients p ON a.patient_id = p.id
JOIN doctors d ON a.doctor_id = d.id
WHERE a.status = 'booked' AND a.requested_datetime > NOW()
ORDER BY a.requested_datetime ASC;

-- View for doctor availability
CREATE OR REPLACE VIEW doctor_availability AS
SELECT
    d.id,
    d.name,
    d.department,
    COUNT(CASE WHEN s.status = 'available' THEN 1 END) as available_slots,
    COUNT(CASE WHEN s.status = 'booked' THEN 1 END) as booked_slots,
    COUNT(s.id) as total_slots
FROM doctors d
LEFT JOIN available_slots s ON d.id = s.doctor_id AND s.date >= CURRENT_DATE
WHERE d.is_active = TRUE
GROUP BY d.id, d.name, d.department
ORDER BY available_slots DESC;

-- View for patient appointment history
CREATE OR REPLACE VIEW patient_appointment_history AS
SELECT
    a.id,
    a.patient_id,
    a.doctor_id,
    d.name AS doctor_name,
    a.reason,
    a.requested_datetime,
    a.status,
    a.created_at
FROM appointments a
JOIN doctors d ON a.doctor_id = d.id
ORDER BY a.created_at DESC;

-- ========================================
-- FUNCTIONS
-- ========================================

-- Function to book appointment and update slot
CREATE OR REPLACE FUNCTION book_appointment(
    p_patient_id UUID,
    p_doctor_id VARCHAR(20),
    p_slot_id UUID,
    p_reason TEXT,
    p_requested_datetime TIMESTAMP
)
RETURNS TABLE (success BOOLEAN, appointment_id UUID, message VARCHAR) AS $$
DECLARE
    v_appointment_id UUID;
BEGIN
    -- Check if slot is available
    IF NOT EXISTS (
        SELECT 1 FROM available_slots
        WHERE id = p_slot_id AND status = 'available' AND doctor_id = p_doctor_id
    ) THEN
        RETURN QUERY SELECT FALSE::BOOLEAN, NULL::UUID, 'Slot is not available'::VARCHAR;
        RETURN;
    END IF;

    -- Create appointment
    INSERT INTO appointments (patient_id, doctor_id, slot_id, reason, status, requested_datetime)
    VALUES (p_patient_id, p_doctor_id, p_slot_id, p_reason, 'booked', p_requested_datetime)
    RETURNING appointments.id INTO v_appointment_id;

    -- Update slot status
    UPDATE available_slots SET status = 'booked' WHERE id = p_slot_id;

    -- Log action
    INSERT INTO audit_logs (action, appointment_id, patient_id, doctor_id, details, status)
    VALUES ('BOOK', v_appointment_id, p_patient_id, p_doctor_id, 'Appointment booked successfully', 'SUCCESS');

    RETURN QUERY SELECT TRUE::BOOLEAN, v_appointment_id::UUID, 'Appointment booked successfully'::VARCHAR;
END;
$$ LANGUAGE plpgsql;

-- Function to cancel appointment
CREATE OR REPLACE FUNCTION cancel_appointment(
    p_appointment_id UUID,
    p_cancellation_reason TEXT
)
RETURNS TABLE (success BOOLEAN, message VARCHAR) AS $$
DECLARE
    v_slot_id UUID;
BEGIN
    -- Get slot ID
    SELECT slot_id INTO v_slot_id FROM appointments WHERE id = p_appointment_id;

    -- Cancel appointment
    UPDATE appointments
    SET status = 'cancelled', cancelled_at = NOW(), cancellation_reason = p_cancellation_reason
    WHERE id = p_appointment_id AND status != 'cancelled';

    -- Update slot status back to available if slot exists
    IF v_slot_id IS NOT NULL THEN
        UPDATE available_slots SET status = 'available' WHERE id = v_slot_id;
    END IF;

    -- Log action
    INSERT INTO audit_logs (action, appointment_id, details, status)
    VALUES ('CANCEL', p_appointment_id, 'Appointment cancelled: ' || COALESCE(p_cancellation_reason, ''), 'SUCCESS');

    RETURN QUERY SELECT TRUE::BOOLEAN, 'Appointment cancelled successfully'::VARCHAR;
END;
$$ LANGUAGE plpgsql;

-- Function to get available slots for a doctor
CREATE OR REPLACE FUNCTION get_available_slots_for_doctor(
    p_doctor_id VARCHAR(20),
    p_from_date DATE,
    p_to_date DATE
)
RETURNS TABLE (
    slot_id UUID,
    date DATE,
    time TIME,
    duration_minutes INTEGER
) AS $$
SELECT id, date, time, duration_minutes
FROM available_slots
WHERE doctor_id = p_doctor_id
  AND status = 'available'
  AND date >= p_from_date
  AND date <= p_to_date
ORDER BY date, time;
$$ LANGUAGE sql;

-- ========================================
-- TRIGGERS
-- ========================================

-- Trigger to update appointment's updated_at timestamp
CREATE OR REPLACE FUNCTION update_appointment_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER appointment_update_timestamp
BEFORE UPDATE ON appointments
FOR EACH ROW
EXECUTE FUNCTION update_appointment_timestamp();

-- Trigger to update doctor's updated_at timestamp
CREATE OR REPLACE FUNCTION update_doctor_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER doctor_update_timestamp
BEFORE UPDATE ON doctors
FOR EACH ROW
EXECUTE FUNCTION update_doctor_timestamp();

-- Trigger to update patient's updated_at timestamp
CREATE OR REPLACE FUNCTION update_patient_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patient_update_timestamp
BEFORE UPDATE ON patients
FOR EACH ROW
EXECUTE FUNCTION update_patient_timestamp();

-- ========================================
-- GRANTS (Optional - for security)
-- ========================================

-- Grant appropriate permissions to application user (ranga)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ranga;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO ranga;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ranga;

-- ========================================
-- SCHEMA SUMMARY
-- ========================================
-- Tables: 10
-- Views: 3
-- Functions: 3
-- Triggers: 3
-- Indexes: 30+
--
-- Key Features:
-- - UUID for patient and appointment IDs (scalable, secure)
-- - Enum types for status fields (data integrity)
-- - Comprehensive constraints and validations
-- - Optimized indexes for common queries
-- - Foreign key relationships with cascade rules
-- - Audit trail for all operations
-- - Views for common queries
-- - Stored procedures for complex operations
-- - Timestamp triggers for tracking changes
-- ========================================


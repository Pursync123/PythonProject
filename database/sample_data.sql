-- PostgreSQL Sample Data SQL Script
-- This script populates the database with realistic sample data for testing
-- Run this directly in PostgreSQL or through a database client

-- Insert Departments
INSERT INTO departments (id, name, description, is_active, created_at) VALUES
('cardiology', 'Cardiology', 'Heart and cardiovascular diseases', true, NOW()),
('orthopedics', 'Orthopedics', 'Bones, joints, and muscles', true, NOW()),
('neurology', 'Neurology', 'Nervous system disorders', true, NOW()),
('general', 'General Practice', 'General medical care', true, NOW()),
('dermatology', 'Dermatology', 'Skin conditions', true, NOW()),
('gynecology', 'Gynecology & Obstetrics', 'Maternity, pregnancy, and female reproductive health', true, NOW()),
('surgery', 'General Surgery', 'General and laparoscopic surgery', true, NOW())
ON CONFLICT DO NOTHING;

-- Insert Doctors
INSERT INTO doctors (id, name, email, department, specialization, experience, phone, bio, is_active, created_at, updated_at) VALUES
('doc001', 'Dr. K. Vineela', 'k.vineela@hospital.com', 'gynecology', 'Obstetrician & Gynecologist, Infertility Specialist & Laparoscopic Surgeon', 10, '+91-95500-32011', 'MBBS, DGO, DNB (Gold Medalist). Obstetrician & Gynecologist, Infertility Specialist & Laparoscopic Surgeon. Timings: 10:30AM - 2PM & 6PM - 8:30PM (Sunday: 10AM to 1PM).', true, NOW(), NOW()),
('doc002', 'Dr. V. Ram Prasad', 'v.ramprasad@hospital.com', 'surgery', 'General & Laparoscopic Surgeon', 12, '+91-95500-32011', 'MBBS, MS. General & Laparoscopic Surgeon. Timings: 7PM - 9PM (Sunday: 10AM to 1PM).', true, NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

-- Insert Patients
INSERT INTO patients (id, first_name, last_name, email, phone, dob, insurance_provider, insurance_id, blood_group, is_active, created_at, updated_at) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'John', 'Smith', 'john.smith@email.com', '+1-555-1001', '1990-05-15', 'BlueCross', 'BC-001-2025', 'O+', true, NOW(), NOW()),
('550e8400-e29b-41d4-a716-446655440002', 'Mary', 'Johnson', 'mary.johnson@email.com', '+1-555-1002', '1985-08-22', 'Aetna', 'AET-002-2025', 'A+', true, NOW(), NOW()),
('550e8400-e29b-41d4-a716-446655440003', 'Robert', 'Williams', 'robert.williams@email.com', '+1-555-1003', '1978-03-10', 'Medicare', 'MED-003-2025', 'B+', true, NOW(), NOW()),
('550e8400-e29b-41d4-a716-446655440004', 'Sarah', 'Brown', 'sarah.brown@email.com', '+1-555-1004', '1992-11-30', 'United Healthcare', 'UHC-004-2025', 'O-', true, NOW(), NOW()),
('550e8400-e29b-41d4-a716-446655440005', 'Michael', 'Davis', 'michael.davis@email.com', '+1-555-1005', '1988-07-18', 'Cigna', 'CIG-005-2025', 'AB+', true, NOW(), NOW()),
('550e8400-e29b-41d4-a716-446655440006', 'Jennifer', 'Taylor', 'jennifer.taylor@email.com', '+1-555-1006', '1995-02-14', 'BlueCross', 'BC-006-2025', 'A-', true, NOW(), NOW()),
('550e8400-e29b-41d4-a716-446655440007', 'David', 'Anderson', 'david.anderson@email.com', '+1-555-1007', '1980-09-25', 'Aetna', 'AET-007-2025', 'B-', true, NOW(), NOW()),
('550e8400-e29b-41d4-a716-446655440008', 'Lisa', 'Martinez', 'lisa.martinez@email.com', '+1-555-1008', '1987-12-03', 'United Healthcare', 'UHC-008-2025', 'AB-', true, NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Insert Available Slots (Next 14 days, multiple slots per doctor per day)
-- Morning slots (9 AM, 10 AM, 11 AM) and Afternoon slots (2 PM, 3 PM, 4 PM)
-- For the 2 doctors

-- Sample slots for doc001 (next 7 days)
INSERT INTO available_slots (id, doctor_id, date, time, duration_minutes, status, created_at, updated_at) VALUES
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '1 day', '10:30:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '1 day', '11:30:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '1 day', '13:00:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '1 day', '18:00:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '1 day', '19:30:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '2 days', '10:30:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '2 days', '12:00:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '2 days', '18:30:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '3 days', '11:00:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc001', CURRENT_DATE + INTERVAL '3 days', '19:00:00', 30, 'available', NOW(), NOW());

-- Sample slots for doc002
INSERT INTO available_slots (id, doctor_id, date, time, duration_minutes, status, created_at, updated_at) VALUES
(gen_random_uuid(), 'doc002', CURRENT_DATE + INTERVAL '1 day', '19:00:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc002', CURRENT_DATE + INTERVAL '1 day', '20:00:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc002', CURRENT_DATE + INTERVAL '2 days', '19:00:00', 30, 'available', NOW(), NOW()),
(gen_random_uuid(), 'doc002', CURRENT_DATE + INTERVAL '2 days', '20:30:00', 30, 'available', NOW(), NOW());

-- Insert Sample Audit Logs
INSERT INTO audit_logs (id, action, patient_id, doctor_id, user_id, details, status, created_at) VALUES
(gen_random_uuid(), 'BOOK', '550e8400-e29b-41d4-a716-446655440001', 'doc001', 'admin', 'Sample data created for testing', 'SUCCESS', NOW()),
(gen_random_uuid(), 'VIEW', '550e8400-e29b-41d4-a716-446655440002', 'doc002', 'user', 'Patient viewed appointment', 'SUCCESS', NOW()),
(gen_random_uuid(), 'BOOK', '550e8400-e29b-41d4-a716-446655440003', 'doc001', 'admin', 'Appointment booked via API', 'SUCCESS', NOW());

-- Verify data insertion
SELECT 'Departments' as type, COUNT(*) as count FROM departments
UNION ALL
SELECT 'Doctors', COUNT(*) FROM doctors
UNION ALL
SELECT 'Patients', COUNT(*) FROM patients
UNION ALL
SELECT 'Available Slots', COUNT(*) FROM available_slots
UNION ALL
SELECT 'Appointments', COUNT(*) FROM appointments
UNION ALL
SELECT 'Audit Logs', COUNT(*) FROM audit_logs;


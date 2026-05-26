from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String(20), default="patient")  # patient | doctor | admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date_of_birth = Column(String(20))
    blood_type = Column(String(5))
    genotype = Column(String(5))
    allergies = Column(Text)
    phone = Column(String(20))
    address = Column(Text)
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))
    qr_token = Column(String, unique=True, default=generate_uuid)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="patient")
    medical_records = relationship("MedicalRecord", back_populates="patient")
    prescriptions = relationship("Prescription", back_populates="patient")
    vaccinations = relationship("Vaccination", back_populates="patient")
    lab_results = relationship("LabResult", back_populates="patient")
    ai_summaries = relationship("AISummary", back_populates="patient")


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    doctor_name = Column(String(100))
    hospital = Column(String(100))
    diagnosis = Column(Text, nullable=False)
    notes = Column(Text)
    visit_date = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="medical_records")
    prescriptions = relationship("Prescription", back_populates="record")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    record_id = Column(String, ForeignKey("medical_records.id"), nullable=True)
    drug_name = Column(String(100), nullable=False)
    dosage = Column(String(50))
    frequency = Column(String(50))
    duration = Column(String(50))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="prescriptions")
    record = relationship("MedicalRecord", back_populates="prescriptions")


class Vaccination(Base):
    __tablename__ = "vaccinations"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    vaccine_name = Column(String(100), nullable=False)
    date_given = Column(String(20))
    next_due = Column(String(20))
    administered_by = Column(String(100))
    location = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="vaccinations")


class LabResult(Base):
    __tablename__ = "lab_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    test_name = Column(String(100), nullable=False)
    result = Column(Text)
    unit = Column(String(30))
    reference_range = Column(String(50))
    is_abnormal = Column(Boolean, default=False)
    lab_name = Column(String(100))
    test_date = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="lab_results")


class AISummary(Base):
    __tablename__ = "ai_summaries"

    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    summary_text = Column(Text, nullable=False)
    risk_flags = Column(Text)
    drug_interactions = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="ai_summaries")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource = Column(String(100))
    details = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
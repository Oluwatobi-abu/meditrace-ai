from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import Patient, User
import qrcode
import base64
from io import BytesIO

router = APIRouter(prefix="/patients", tags=["Patients"])


# --- Pydantic models ---

class PatientProfileUpdate(BaseModel):
    date_of_birth: Optional[str] = None
    blood_type: Optional[str] = None
    genotype: Optional[str] = None
    allergies: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


# --- Routes ---

@router.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return {
        "id": patient.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "date_of_birth": patient.date_of_birth,
        "blood_type": patient.blood_type,
        "genotype": patient.genotype,
        "allergies": patient.allergies,
        "phone": patient.phone,
        "address": patient.address,
        "emergency_contact": patient.emergency_contact,
        "emergency_phone": patient.emergency_phone,
        "qr_token": patient.qr_token,
        "created_at": patient.created_at
    }


@router.put("/me")
def update_my_profile(data: PatientProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return {"message": "Profile updated successfully", "patient_id": patient.id}


@router.get("/me/qr")
def get_my_qr_code(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Generate QR code pointing to emergency endpoint
    emergency_url = f"http://127.0.0.1:8000/emergency/{patient.qr_token}"
    qr = qrcode.make(emergency_url)

    # Convert to base64 so frontend can display it as an image
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "qr_token": patient.qr_token,
        "emergency_url": emergency_url,
        "qr_image": f"data:image/png;base64,{qr_base64}"
    }


@router.get("/all")
def get_all_patients(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    patients = db.query(Patient).all()
    return [{"id": p.id, "user_id": p.user_id, "blood_type": p.blood_type, "qr_token": p.qr_token} for p in patients]
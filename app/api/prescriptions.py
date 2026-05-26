from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import Prescription, Patient, User

router = APIRouter(prefix="/prescriptions", tags=["Prescriptions"])


class PrescriptionCreate(BaseModel):
    drug_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    notes: Optional[str] = None
    record_id: Optional[str] = None


@router.post("/", status_code=201)
def add_prescription(data: PrescriptionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    prescription = Prescription(
        patient_id=patient.id,
        drug_name=data.drug_name,
        dosage=data.dosage,
        frequency=data.frequency,
        duration=data.duration,
        notes=data.notes,
        record_id=data.record_id
    )
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    return {"message": "Prescription added", "prescription_id": prescription.id}


@router.get("/")
def get_my_prescriptions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient.id).order_by(Prescription.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "drug_name": p.drug_name,
            "dosage": p.dosage,
            "frequency": p.frequency,
            "duration": p.duration,
            "notes": p.notes,
            "is_active": p.is_active,
            "created_at": p.created_at
        }
        for p in prescriptions
    ]


@router.put("/{prescription_id}/deactivate")
def deactivate_prescription(prescription_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.patient_id == patient.id
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    prescription.is_active = False
    db.commit()
    return {"message": "Prescription deactivated"}


@router.delete("/{prescription_id}")
def delete_prescription(prescription_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    prescription = db.query(Prescription).filter(
        Prescription.id == prescription_id,
        Prescription.patient_id == patient.id
    ).first()
    if not prescription:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(prescription)
    db.commit()
    return {"message": "Prescription deleted"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import MedicalRecord, Patient, User

router = APIRouter(prefix="/records", tags=["Medical Records"])


# --- Pydantic models ---

class RecordCreate(BaseModel):
    diagnosis: str
    doctor_name: Optional[str] = None
    hospital: Optional[str] = None
    notes: Optional[str] = None
    visit_date: Optional[str] = None


class RecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    doctor_name: Optional[str] = None
    hospital: Optional[str] = None
    notes: Optional[str] = None
    visit_date: Optional[str] = None


# --- Routes ---

@router.post("/", status_code=201)
def create_record(data: RecordCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    record = MedicalRecord(
        patient_id=patient.id,
        diagnosis=data.diagnosis,
        doctor_name=data.doctor_name,
        hospital=data.hospital,
        notes=data.notes,
        visit_date=data.visit_date
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"message": "Medical record created", "record_id": record.id}


@router.get("/")
def get_my_records(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).order_by(MedicalRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "diagnosis": r.diagnosis,
            "doctor_name": r.doctor_name,
            "hospital": r.hospital,
            "notes": r.notes,
            "visit_date": r.visit_date,
            "created_at": r.created_at
        }
        for r in records
    ]


@router.get("/{record_id}")
def get_record(record_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.patient_id == patient.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "id": record.id,
        "diagnosis": record.diagnosis,
        "doctor_name": record.doctor_name,
        "hospital": record.hospital,
        "notes": record.notes,
        "visit_date": record.visit_date,
        "created_at": record.created_at
    }


@router.put("/{record_id}")
def update_record(record_id: str, data: RecordUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.patient_id == patient.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return {"message": "Record updated", "record_id": record.id}


@router.delete("/{record_id}")
def delete_record(record_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    record = db.query(MedicalRecord).filter(
        MedicalRecord.id == record_id,
        MedicalRecord.patient_id == patient.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}
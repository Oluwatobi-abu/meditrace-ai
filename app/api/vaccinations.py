from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import Vaccination, Patient, User

router = APIRouter(prefix="/vaccinations", tags=["Vaccinations"])


class VaccinationCreate(BaseModel):
    vaccine_name: str
    date_given: Optional[str] = None
    next_due: Optional[str] = None
    administered_by: Optional[str] = None
    location: Optional[str] = None


@router.post("/", status_code=201)
def add_vaccination(data: VaccinationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    vaccination = Vaccination(
        patient_id=patient.id,
        vaccine_name=data.vaccine_name,
        date_given=data.date_given,
        next_due=data.next_due,
        administered_by=data.administered_by,
        location=data.location
    )
    db.add(vaccination)
    db.commit()
    db.refresh(vaccination)
    return {"message": "Vaccination record added", "vaccination_id": vaccination.id}


@router.get("/")
def get_my_vaccinations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    vaccinations = db.query(Vaccination).filter(Vaccination.patient_id == patient.id).order_by(Vaccination.created_at.desc()).all()
    return [
        {
            "id": v.id,
            "vaccine_name": v.vaccine_name,
            "date_given": v.date_given,
            "next_due": v.next_due,
            "administered_by": v.administered_by,
            "location": v.location,
            "created_at": v.created_at
        }
        for v in vaccinations
    ]


@router.delete("/{vaccination_id}")
def delete_vaccination(vaccination_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    vaccination = db.query(Vaccination).filter(
        Vaccination.id == vaccination_id,
        Vaccination.patient_id == patient.id
    ).first()
    if not vaccination:
        raise HTTPException(status_code=404, detail="Vaccination not found")
    db.delete(vaccination)
    db.commit()
    return {"message": "Vaccination record deleted"}
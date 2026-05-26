from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import LabResult, Patient, User

router = APIRouter(prefix="/labs", tags=["Lab Results"])


class LabResultCreate(BaseModel):
    test_name: str
    result: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    is_abnormal: Optional[bool] = False
    lab_name: Optional[str] = None
    test_date: Optional[str] = None


@router.post("/", status_code=201)
def add_lab_result(data: LabResultCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    lab = LabResult(
        patient_id=patient.id,
        test_name=data.test_name,
        result=data.result,
        unit=data.unit,
        reference_range=data.reference_range,
        is_abnormal=data.is_abnormal,
        lab_name=data.lab_name,
        test_date=data.test_date
    )
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return {"message": "Lab result added", "lab_id": lab.id}


@router.get("/")
def get_my_labs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    labs = db.query(LabResult).filter(LabResult.patient_id == patient.id).order_by(LabResult.created_at.desc()).all()
    return [
        {
            "id": l.id,
            "test_name": l.test_name,
            "result": l.result,
            "unit": l.unit,
            "reference_range": l.reference_range,
            "is_abnormal": l.is_abnormal,
            "lab_name": l.lab_name,
            "test_date": l.test_date,
            "created_at": l.created_at
        }
        for l in labs
    ]


@router.delete("/{lab_id}")
def delete_lab_result(lab_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    lab = db.query(LabResult).filter(
        LabResult.id == lab_id,
        LabResult.patient_id == patient.id
    ).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab result not found")
    db.delete(lab)
    db.commit()
    return {"message": "Lab result deleted"}
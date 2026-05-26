from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import Patient, MedicalRecord, Prescription, Vaccination, LabResult, AISummary, User

router = APIRouter(prefix="/emergency", tags=["Emergency Access"])


@router.get("/{qr_token}")
def emergency_access(qr_token: str, db: Session = Depends(get_db)):
    """
    Public endpoint — no login required.
    Accessed by scanning a patient's QR code in an emergency.
    Returns only critical, life-saving information.
    """
    patient = db.query(Patient).filter(Patient.qr_token == qr_token).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found. Invalid QR code.")

    user = db.query(User).filter(User.id == patient.user_id).first()

    # Active prescriptions only
    active_prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient.id,
        Prescription.is_active == True
    ).all()

    # Recent medical records (last 5)
    recent_records = db.query(MedicalRecord).filter(
        MedicalRecord.patient_id == patient.id
    ).order_by(MedicalRecord.created_at.desc()).limit(5).all()

    # All vaccinations
    vaccinations = db.query(Vaccination).filter(
        Vaccination.patient_id == patient.id
    ).all()

    # Abnormal lab results only
    abnormal_labs = db.query(LabResult).filter(
        LabResult.patient_id == patient.id,
        LabResult.is_abnormal == True
    ).all()

    # Latest AI summary
    latest_summary = db.query(AISummary).filter(
        AISummary.patient_id == patient.id
    ).order_by(AISummary.generated_at.desc()).first()

    return {
        "emergency_profile": {
            "full_name": user.full_name if user else "Unknown",
            "blood_type": patient.blood_type,
            "genotype": patient.genotype,
            "allergies": patient.allergies,
            "emergency_contact": patient.emergency_contact,
            "emergency_phone": patient.emergency_phone,
        },
        "active_medications": [
            {
                "drug_name": p.drug_name,
                "dosage": p.dosage,
                "frequency": p.frequency
            }
            for p in active_prescriptions
        ],
        "recent_diagnoses": [
            {
                "diagnosis": r.diagnosis,
                "hospital": r.hospital,
                "visit_date": r.visit_date,
                "doctor": r.doctor_name
            }
            for r in recent_records
        ],
        "vaccinations": [
            {
                "vaccine": v.vaccine_name,
                "date_given": v.date_given,
                "next_due": v.next_due
            }
            for v in vaccinations
        ],
        "abnormal_labs": [
            {
                "test": l.test_name,
                "result": l.result,
                "unit": l.unit,
                "reference_range": l.reference_range
            }
            for l in abnormal_labs
        ],
        "ai_summary": latest_summary.summary_text if latest_summary else "No AI summary generated yet. Visit /ai/summary to generate one.",
        "disclaimer": "This information is provided for emergency medical use only via MediTrace AI."
    }
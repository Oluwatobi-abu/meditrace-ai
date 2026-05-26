from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.schemas import Patient, MedicalRecord, Prescription, Vaccination, LabResult, AISummary, User
from app.core.config import settings
from groq import Groq
import uuid

router = APIRouter(prefix="/ai", tags=["AI"])

client = Groq(api_key=settings.GROQ_API_KEY)


def build_patient_context(patient, records, prescriptions, vaccinations, labs):
    context = f"""
PATIENT MEDICAL PROFILE:
- Blood Type: {patient.blood_type or 'Unknown'}
- Genotype: {patient.genotype or 'Unknown'}
- Known Allergies: {patient.allergies or 'None reported'}

MEDICAL HISTORY ({len(records)} records):
"""
    for r in records:
        context += f"- [{r.visit_date or 'Unknown date'}] {r.diagnosis} at {r.hospital or 'Unknown hospital'} by Dr. {r.doctor_name or 'Unknown'}. Notes: {r.notes or 'None'}\n"

    context += f"\nACTIVE PRESCRIPTIONS ({len([p for p in prescriptions if p.is_active])}):\n"
    for p in prescriptions:
        if p.is_active:
            context += f"- {p.drug_name} | {p.dosage or 'N/A'} | {p.frequency or 'N/A'} | Duration: {p.duration or 'N/A'}\n"

    context += f"\nVACCINATION HISTORY ({len(vaccinations)} vaccines):\n"
    for v in vaccinations:
        context += f"- {v.vaccine_name} given on {v.date_given or 'Unknown date'}, next due: {v.next_due or 'N/A'}\n"

    context += f"\nRECENT LAB RESULTS ({len(labs)} tests):\n"
    for l in labs:
        abnormal = "⚠️ ABNORMAL" if l.is_abnormal else "Normal"
        context += f"- {l.test_name}: {l.result or 'N/A'} {l.unit or ''} [{abnormal}] | Ref: {l.reference_range or 'N/A'}\n"

    return context


@router.post("/summary")
def generate_ai_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    records = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).all()
    prescriptions = db.query(Prescription).filter(Prescription.patient_id == patient.id).all()
    vaccinations = db.query(Vaccination).filter(Vaccination.patient_id == patient.id).all()
    labs = db.query(LabResult).filter(LabResult.patient_id == patient.id).all()

    context = build_patient_context(patient, records, prescriptions, vaccinations, labs)

    prompt = f"""You are a clinical AI assistant for MediTrace AI, an emergency health record platform in Africa.

Given the following patient medical profile, generate:
1. A concise clinical summary (3-5 sentences) suitable for an emergency room doctor
2. Critical alerts (allergies, abnormal labs, high-risk conditions) — be direct and urgent
3. Drug interaction warnings for current active medications
4. Recommended precautions for emergency treatment

Be clear, clinical, and concise. Use plain English — not overly technical.

{context}

Respond in this exact format:
CLINICAL SUMMARY:
[summary here]

CRITICAL ALERTS:
[alerts here, or "None identified"]

DRUG INTERACTIONS:
[interactions here, or "None identified"]

EMERGENCY PRECAUTIONS:
[precautions here]
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        summary_text = response.choices[0].message.content

        # Save summary to database
        summary = AISummary(
            id=str(uuid.uuid4()),
            patient_id=patient.id,
            summary_text=summary_text,
            risk_flags="See summary",
            drug_interactions="See summary"
        )
        db.add(summary)
        db.commit()

        return {
            "summary": summary_text,
            "generated_at": summary.generated_at,
            "patient_name": current_user.full_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.get("/summaries")
def get_past_summaries(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    summaries = db.query(AISummary).filter(AISummary.patient_id == patient.id).order_by(AISummary.generated_at.desc()).all()
    return [
        {
            "id": s.id,
            "summary_text": s.summary_text,
            "generated_at": s.generated_at
        }
        for s in summaries
    ]
# MediTrace AI 🏥

> **AI-powered emergency health record platform for Africa**  
> Built for the [#BuildQuik Challenge](https://lu.ma/cnk0mtop) · May 2026

<div align="center">

![MediTrace AI](https://img.shields.io/badge/MediTrace-AI%20Health%20Records-00d4aa?style=for-the-badge&logo=heart&logoColor=white)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/AI-Groq%20%C2%B7%20Llama%203.3-7F77DD?style=flat-square)](https://groq.com)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![QuikDB](https://img.shields.io/badge/Deploy-QuikDB%20Compute-FF6B35?style=flat-square)](https://compute.quikdb.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**[Live Demo](#) · [API Docs](#) · [#BuildQuik](https://lu.ma/cnk0mtop)**

</div>

---

## 🚨 The Problem

Nigerian patients **lose paper records**. Hospitals **cannot share medical history** across facilities. Emergencies become dangerous because critical information — blood type, allergies, active medications — is unavailable when it matters most.

> *"Every year, preventable deaths occur in African emergency rooms because a doctor didn't know the patient was allergic to penicillin."*

**MediTrace AI solves this.**

---

## ✨ What It Does

MediTrace AI is a national emergency health record platform where patients, doctors, and hospitals share **one single source of medical truth** — surfaced instantly via QR code when seconds count.

| Feature | Description |
|---|---|
| 🩸 **Emergency Profile** | Blood type, genotype, allergies — always accessible |
| 💊 **Prescriptions** | Active medications with drug interaction warnings |
| 💉 **Vaccination History** | Full immunisation record with next-due dates |
| 🔬 **Lab Results** | Test history with abnormal result flagging |
| 🤖 **AI Clinical Summary** | Groq Llama 3.3 generates a clinical brief in seconds |
| 📱 **QR Emergency Card** | Scan → instant profile. No login. No friction. |
| 👨‍⚕️ **Doctor Access Panel** | Role-based access for medical professionals |
| 📊 **Audit Logs** | Every access tracked for accountability |

---

## 🎬 Demo Flow

```
1. Patient registers → builds health profile (blood type, allergies, medications)
2. Doctor logs diagnosis, prescriptions, lab results
3. AI generates clinical summary with drug interaction warnings
4. Patient receives a unique QR code card
5. Emergency → nurse scans QR → INSTANT full medical history
   No login. No app. No friction.
```

---

## 🛠 Tech Stack

```
Backend      →  FastAPI (Python 3.11)
Database     →  PostgreSQL via Supabase
AI Engine    →  Groq API · Llama 3.3 70B Versatile
Auth         →  JWT (python-jose + passlib[bcrypt])
QR Code      →  qrcode[pil] (Python)
Deployment   →  QuikDB Compute
Frontend     →  Vanilla HTML · CSS · JavaScript
```

---

## 🗄 Database Schema

8 relational tables — designed for real healthcare data engineering:

```
users
  └── patients
        ├── medical_records
        │     └── prescriptions
        ├── vaccinations
        ├── lab_results
        ├── ai_summaries
        └── (audit_logs ← users)
```

| Table | Purpose |
|---|---|
| `users` | Auth, roles (patient / doctor / admin) |
| `patients` | Medical profile, QR token, emergency contacts |
| `medical_records` | Diagnoses, doctor notes, hospital visits |
| `prescriptions` | Drug name, dosage, frequency, active status |
| `vaccinations` | Vaccine history, next due dates |
| `lab_results` | Test results, abnormal flagging |
| `ai_summaries` | Stored AI-generated clinical summaries |
| `audit_logs` | Who accessed what and when |

---

## 🔌 API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register patient or doctor |
| `POST` | `/auth/login` | ❌ | Get JWT token |
| `GET` | `/auth/me` | ✅ | Current user info |
| `GET` | `/patients/me` | ✅ | Get patient profile |
| `PUT` | `/patients/me` | ✅ | Update patient profile |
| `GET` | `/patients/me/qr` | ✅ | Generate QR code |
| `CRUD` | `/records/` | ✅ | Medical records |
| `CRUD` | `/prescriptions/` | ✅ | Prescriptions |
| `CRUD` | `/vaccinations/` | ✅ | Vaccination history |
| `CRUD` | `/labs/` | ✅ | Lab results |
| `POST` | `/ai/summary` | ✅ | Generate AI clinical summary |
| `GET` | `/emergency/{token}` | ❌ | **Public QR emergency access** |
| `GET` | `/health` | ❌ | Health check |

> Full interactive docs at `/docs` (Swagger UI) and `/redoc`
> 💡 Note on Public Endpoints
> ❌ Public endpoints are intentionally open by design:
> registration/login require no prior auth by nature,
> the emergency endpoint is public so any nurse can
> scan a QR code without a MediTrace account.

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database (Supabase free tier works)
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Oluwatobi-abu/meditrace-ai.git
cd meditrace-ai

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your real credentials

# 5. Run the development server
uvicorn app.main:app --reload
```

### Access Points
| URL | Description |
|---|---|
| `http://127.0.0.1:8000` | Patient dashboard (local) |
| `http://127.0.0.1:8000/docs` | Swagger API docs (local) |
| `http://127.0.0.1:8000/health` | Health check (local) |

---

## 🌍 Live Demo

| URL | Description |
|---|---|
| `https://meditrace-ai.quikdb.net` | Live patient dashboard |
| `https://meditrace-ai.quikdb.net/docs` | Live API documentation |
| `https://meditrace-ai.quikdb.net/health` | Live health check |
| `https://meditrace-ai.quikdb.net/static/emergency.html?token={qr_token}` | Emergency QR access |

> Deployed on QuikDB Compute · Python 3.11 · West EU region

---

## 🔐 Environment Variables

```env
# Database (PostgreSQL connection string)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Authentication
SECRET_KEY=your-super-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Engine
GROQ_API_KEY=gsk_your_groq_api_key_here

# App Config
APP_NAME=MediTrace AI
DEBUG=False
```

---

## 📁 Project Structure

```
meditrace-ai/
├── app/
│   ├── api/
│   │   ├── auth.py          # JWT auth, login, register
│   │   ├── patients.py      # Patient CRUD + QR generation
│   │   ├── records.py       # Medical records
│   │   ├── prescriptions.py # Prescription management
│   │   ├── vaccinations.py  # Vaccination history
│   │   ├── labs.py          # Lab results
│   │   ├── ai.py            # Groq AI summary engine
│   │   └── emergency.py     # Public QR emergency endpoint
│   ├── core/
│   │   ├── config.py        # Environment settings
│   │   ├── database.py      # SQLAlchemy + PostgreSQL
│   │   └── security.py      # Password hashing, JWT utils
│   ├── models/
│   │   └── schemas.py       # All 8 database table models
│   └── main.py              # FastAPI app entry point
├── frontend/
│   ├── index.html           # Patient dashboard (SPA)
│   └── emergency.html       # Public QR emergency page
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container config
├── quikdb.json              # QuikDB Compute config
└── README.md
```

---

## 👨‍💻 Built By

**Abubakar Oluwatobi**  
Python Developer  |  Data Science  · Lagos, Nigeria

[![GitHub](https://img.shields.io/badge/GitHub-Oluwatobi--abu-181717?style=flat-square&logo=github)](https://github.com/Oluwatobi-abu)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-abubakaroluwatobi-0077B5?style=flat-square&logo=linkedin)](https://linkedin.com/in/abubakaroluwatobi)

---

## 🗺 Roadmap

The current MVP focuses on the core emergency access use case. Planned features for future versions:

- [ ] Hospital-scoped doctor access (HL7 FHIR consent model) — doctors see only patients affiliated with their facility
- [ ] Doctor-initiated record creation — verified doctors append records directly to a patient's file
- [ ] Patient notification system — alerts when a doctor views or updates your record
- [ ] Offline-first mobile app — access emergency profile even without internet
- [ ] NDPR compliance audit log export — full data access report for regulatory compliance
- [ ] Multi-language support — Hausa, Yoruba, Igbo interfaces
- [ ] Integration with NHIA (National Health Insurance Authority) database

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built for #BuildQuik Challenge · QuikDB · May 2026**

*Securing African Healthcare — one QR code at a time.* 🏥

</div>

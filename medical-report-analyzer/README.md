# 🏥 AI-Based Medical Report Analyzer

> An intelligent full-stack system for uploading medical lab reports, automatically extracting structured data, predicting disease risks, and providing AI-powered health insights — designed for both patients and their doctors.

---

## 📋 Table of Contents

- [Project Purpose & Key Features](#-project-purpose--key-features)
- [Full Tech Stack](#-full-tech-stack)
- [Folder Structure Overview](#-folder-structure-overview)
- [Environment Variables](#-environment-variables)
- [Running the Backend](#-running-the-backend-locally)
- [Running the Frontend](#-running-the-frontend-locally)
- [MongoDB Atlas Setup](#-mongodb-atlas-setup)
- [Optional Ollama Setup](#-optional-ollama-setup)
- [Docker Compose](#-running-with-docker-compose)
- [MVP Scope vs Future Modules](#-mvp-scope-vs-future-modules)
- [Development Roadmap](#-development-roadmap)

---

## 🎯 Project Purpose & Key Features

### Purpose
Patients generate medical lab reports regularly, but most people lack the medical expertise to understand them. This system bridges that gap by:

1. **Accepting PDF uploads** of medical lab reports
2. **Extracting all text** from the PDF (text-layer or scanned)
3. **Sending the text to Gemini AI** to produce a structured analysis
4. **Predicting disease risks** (diabetes, CKD, anemia, cardiovascular) using ML models
5. **Presenting results** in a clear, patient-friendly dashboard
6. **Allowing doctors** to view their patients' reports securely

### Key Features (MVP — Phase 1)
| Feature | Status |
|---------|--------|
| Patient registration & JWT authentication | ✅ Complete |
| Doctor registration with unique doctor_id | ✅ Complete |
| PDF medical report upload | ✅ Complete |
| Text extraction via PyMuPDF / pdfplumber | ✅ Complete |
| Offline report analysis | ✅ Complete |
| Ollama-powered report analysis | ✅ Optional |
| Patient dashboard | ✅ Complete |
| Doctor dashboard with patient management | ✅ Complete |
| Doctor–patient connection and chat | ✅ Complete |
| GPS-based nearby doctor discovery | ✅ Complete |

---

## 🛠 Full Tech Stack

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10+ | Core language |
| FastAPI | 0.111.0 | Async web framework |
| Uvicorn | 0.29.0 | ASGI server |
| Motor | 3.4.0 | Async MongoDB driver |
| Beanie ODM | 1.26.0 | Typed MongoDB document models |
| Pydantic | 2.7.1 | Data validation & serialization |
| pydantic-settings | 2.2.1 | Settings from environment |
| python-jose | 3.3.0 | JWT creation & verification |
| passlib[bcrypt] | 1.7.4 | Password hashing |
| python-multipart | 0.0.9 | File upload support |
| python-dotenv | 1.0.1 | .env file loading |
| httpx | 0.27.0 | Ollama API client |
| PyMuPDF | 1.24.3 | Primary PDF text extraction |
| pdfplumber | 0.11.0 | Fallback PDF extraction |
| httpx | 0.27.0 | Async HTTP client |
| pytest | 8.2.0 | Test framework |
| pytest-asyncio | 0.23.6 | Async test support |

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18.3.x | UI framework |
| TypeScript | 5.4.x | Type safety |
| Vite | 5.2.x | Build tool & dev server |
| React Router | 6.23.x | Client-side routing |
| Axios | 1.7.x | HTTP client |
| TailwindCSS | 3.4.x | Utility-first CSS framework |
| React Hook Form | 7.51.x | Form state management |
| Zod | 3.23.x | Schema validation |

### Database
| Technology | Purpose |
|-----------|---------|
| MongoDB Atlas | Cloud-hosted NoSQL database |
| Motor | Async Python driver |
| Beanie ODM | Typed document models over Motor |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| Docker + Docker Compose | Container orchestration |
| .env files | Secret & config management |
| Local filesystem | MVP file storage (`backend/uploads/`) |

---

## 📁 Folder Structure Overview

```
medical-report-analyzer/
├── frontend/                    # React + Vite + TypeScript
│   └── src/
│       ├── components/          # Reusable UI components
│       │   ├── common/          # Navbar, Sidebar, ProtectedRoute, etc.
│       │   ├── auth/            # LoginForm, RegisterForm
│       │   ├── patient/         # ReportUpload, DiseaseRiskCard, etc.
│       │   └── doctor/          # PatientList, RequestCard, etc.
│       ├── pages/               # Route-level page components
│       ├── layouts/             # Page wrapper layouts
│       ├── context/             # AuthContext (global auth state)
│       ├── hooks/               # useAuth, useReportUpload
│       ├── services/            # Axios API calls (api.ts, authService.ts, ...)
│       ├── types/               # TypeScript interfaces
│       └── utils/               # Shared helper functions
│
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app + lifespan + CORS + routers
│       ├── api/
│       │   ├── dependencies.py  # JWT auth guards, role checks
│       │   └── routes/          # auth, doctors, patients, reports, analysis
│       ├── models/              # Beanie document models (MongoDB collections)
│       ├── schemas/             # Pydantic request/response schemas
│       ├── services/            # Business logic layer
│       ├── ai/
│       │   ├── gemini/          # Gemini client + prompt templates
│       │   ├── ocr/             # Future: PaddleOCR pipeline
│       │   ├── nlp/             # Future: BioBERT NER
│       │   ├── disease_prediction/ # Future: XGBoost/LightGBM models
│       │   └── explainability/  # Future: SHAP
│       ├── core/                # config.py, database.py, security.py
│       └── utils/               # file_utils.py, response_utils.py
│   ├── tests/                   # pytest test suite
│   ├── uploads/                 # Local PDF storage (gitignored)
│   ├── requirements.txt
│   └── .env.example
│
├── data/                        # Future: training datasets
├── models/                      # Future: ML model weights
├── notebooks/                   # Future: EDA and training notebooks
├── scripts/                     # Future: data prep scripts
├── docs/                        # Future: API docs and architecture diagrams
├── docker/
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🔐 Environment Variables

Copy `backend/.env.example` to `backend/.env`. The defaults run without external services.

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URL` | Production | Full MongoDB Atlas connection string |
| `DATABASE_NAME` | ✅ | MongoDB database name (default: `medical_report_analyzer`) |
| `USE_IN_MEMORY_DB` | ✅ | `true` for zero-setup local use; `false` for MongoDB |
| `SECRET_KEY` | ✅ | Secret key for JWT signing — use `openssl rand -hex 32` |
| `ALGORITHM` | ✅ | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ✅ | Token lifetime in minutes (default: `30`) |
| `AI_MODE` | ✅ | `offline` or `ollama` |
| `OLLAMA_BASE_URL` | Ollama only | Local Ollama service URL |
| `OLLAMA_MODEL` | Ollama only | Installed model name |
| `ALLOWED_ORIGINS` | ✅ | CORS allowed origins (default: `http://localhost:5173`) |
| `UPLOAD_DIR` | ✅ | Directory for uploaded files (default: `uploads`) |
| `MAX_FILE_SIZE_MB` | ✅ | Upload size limit in MB (default: `10`) |
| `ENVIRONMENT` | ✅ | `development` / `staging` / `production` |

---

## 🚀 Running the Backend Locally

### Prerequisites
- Python 3.10+
- pip
- MongoDB Atlas only when persistent storage is required
- Ollama only when local LLM analysis is required

### Steps

```bash
# 1. Navigate to the backend directory
cd medical-report-analyzer/backend

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env     # Windows
# cp .env.example .env     # macOS/Linux
# The default file uses an in-memory database and offline analysis.

# 5. Create the uploads directory (if it doesn't exist)
mkdir -p uploads

# 6. Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ⚛️ Running the Frontend Locally

### Prerequisites
- Node.js 18+ and npm

### Steps

```bash
# 1. Navigate to the frontend directory
cd medical-report-analyzer/frontend

# 2. Install dependencies
npm install

# 3. (Optional) Create a frontend .env file for environment variables
# Create frontend/.env.local:
# VITE_API_BASE_URL=http://localhost:8000

# 4. Start the Vite dev server
npm run dev
```

The frontend will be available at: **http://localhost:5173**

> **Note**: The Vite dev server is configured with a proxy. All requests to `/auth`, `/doctors`, `/patients`, `/reports`, `/analysis`, and `/health` are automatically forwarded to `http://localhost:8000`.

---

## 🌐 MongoDB Atlas Setup

1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com) and create a free account.
2. Create a new **Project**.
3. Click **"Build a Database"** → Select **M0 Free Tier** → Choose your region.
4. Set up a **Database User**:
   - Username: `your_username`
   - Password: generate a secure password (save it!)
5. Under **Network Access**, click **"Add IP Address"** → select **"Allow Access from Anywhere"** (0.0.0.0/0) for development.
6. Click **Connect** → **"Connect your application"** → **Python / Motor**.
7. Copy the connection string. Replace `<password>` with your actual password and `<dbname>` with `medical_report_analyzer`.
8. Paste this URL as `MONGODB_URL` in your `backend/.env` file.

---

## 🤖 Optional Ollama Setup

The backend defaults to conservative offline extraction and does not make clinical
risk predictions. For local LLM analysis, install Ollama, download a model, and set:

```env
AI_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

---

## 🐳 Running with Docker Compose

### Prerequisites
- Docker Desktop installed and running

### Steps

```bash
# 1. Navigate to the project root
cd medical-report-analyzer

# 2. Ensure backend/.env exists with all required values
# (copy from .env.example and fill in real values)

# 3. Build and start all services
docker compose up --build

# 4. To run in detached (background) mode:
docker compose up --build -d

# 5. To stop services:
docker compose down
```

**Services:**
| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |

> **Note**: MongoDB is hosted on Atlas — no local MongoDB container is needed or included.

---

## 📦 MVP Scope vs Future Modules

### ✅ MVP (Phase 1 — Current)
- User registration & JWT authentication (patient + doctor roles)
- Doctor profile with unique doctor_id
- Doctor–patient connection request system
- Medical PDF report upload (local storage)
- PDF text extraction: PyMuPDF → pdfplumber fallback
- AI analysis via Google Gemini 1.5 Flash
- Structured data extraction (parameters, risks, recommendations)
- Patient dashboard (upload, view analysis)
- Doctor dashboard (manage patients, view reports)

### 🔜 Phase 2 — Advanced OCR & NER
- PaddleOCR 2.7 + PaddlePaddle for scanned/image PDFs
- OpenCV 4.8 preprocessing (denoising, deskewing, contrast)
- BioBERT / ClinicalBERT NER for medical entity extraction
- Support for multi-page reports and complex layouts

### 🔮 Phase 3 — ML Disease Prediction & Explainability
- XGBoost + LightGBM disease prediction models:
  - Diabetes (HbA1c, FPG, BMI)
  - Chronic Kidney Disease (creatinine, eGFR, BUN)
  - Anemia (hemoglobin, MCV, MCH)
  - Cardiovascular risk (cholesterol, LDL, HDL)
- SHAP TreeExplainer for transparent predictions
- MLflow for model versioning and experiment tracking
- PDF report generation (reportlab / WeasyPrint)
- AWS S3 or Cloudinary for scalable file storage

---

## 🗺 Development Roadmap

```
Phase 1 (MVP)          Phase 2 (OCR/NER)      Phase 3 (ML Models)
─────────────          ─────────────────       ───────────────────
Auth system      →     PaddleOCR pipeline →    Disease prediction
Report upload          OpenCV preprocessing    SHAP explanations
PyMuPDF extract        BioBERT NER             MLflow tracking
Gemini AI              Scanned PDF support     PDF report export
Patient dashboard      Improved accuracy       S3 file storage
Doctor dashboard       Multi-page support      Production deploy
```

**Current Phase**: ✅ **Phase 1 MVP complete**

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow the architecture rules: Routes → Services → AI/Database
4. Add tests for new endpoints in `backend/tests/`
5. Open a Pull Request

---

## 📄 License

This project is for educational and research purposes.

# CrimeIntel AI: Evidence Analysis & Investigation Support

CrimeIntel AI is a secure, intelligent, multi-modal decision support system built for police departments and crime investigators. It helps collect, catalog, analyze, and visualize evidence from active FIRs, leveraging machine learning, graph link analysis, NLP document entity extraction, and OpenStreetMap hotspots.

> [!IMPORTANT]
> **Ethical & Legal Boundary**: Under Indian Police Acts and general criminal justice guidelines, the system **never** declares a suspect guilty. It generates probabilistic leads, MO similarity matches, and risk scores, leaving all final tactical and judicial determinations to authorized human officers.

---

## 💻 Tech Stack

- **Backend Node**: Python, FastAPI, Uvicorn, SQLAlchemy (SQLite / PostgreSQL)
- **Document Store**: local JSON / MongoDB (dual-mode)
- **Relationship Graph**: local NetworkX / Neo4j (dual-mode)
- **Reporting Engine**: ReportLab (official PDF generation)
- **Frontend Console**: React 18, Tailwind CSS, Chart.js, Leaflet.js

---

## 📁 Directory Structure

```text
CrimeIntel AI/
├── backend/
│   ├── app/
│   │   ├── auth/            # JWT validation & password hashing
│   │   ├── ml/              # CV Detector, NER, MO Similarity, Graph links
│   │   ├── models/          # SQL tables and Pydantic schemas
│   │   ├── routers/         # REST API endpoints (Case, Vault, Intel, Chat)
│   │   ├── utils/           # Audit logging, PDF reports, Seeder script
│   │   ├── static/          # Embedded SPA rendering React directly via CDN
│   │   └── main.py          # FastAPI application entry
│   ├── requirements.txt
│   └── run.py               # Startup script
├── frontend/
│   ├── src/                 # Modular React development files
│   │   ├── components/      # Sidebar, Navbar, SVG graphs
│   │   ├── context/         # AuthContext JWT hook
│   │   ├── utils/           # Axios helper
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml       # Production deployment script
└── README.md                # System documentation
```

---

## 🚀 Installation & Quick Start

Since your system does not currently have Node/npm configured in the PATH, we have engineered an **embedded React SPA served directly by FastAPI**. This allows you to run the entire 18-page dashboard, mapping system, chatbots, and PDF generator out-of-the-box with **only a Python installation**.

### Step 1: Install Python Dependencies
Open PowerShell or your terminal in the root directory and install the packages:

```powershell
pip install -r backend/requirements.txt
```

### Step 2: Start the Backend & Frontend Node
Run the startup script:

```powershell
python backend/run.py
```

This launches the server at `http://127.0.0.1:8000`. 

### Step 3: Access the Console
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

Log in using the seeded secure credentials:
- **Username**: `officer_sharma`
- **Password**: `password123`

---

## 🧪 Testing Guide

We have integrated auto-seeding which creates sample cases (e.g. Heists, Ransomware Attacks, Expressways Hijackings) on boot. You can test key features immediately:

1. **Verify Login**: Authenticate as `officer_sharma`. Check the Dashboard telemetry count updates.
2. **Upload Evidence**: Navigate to the Evidence Vault, select the Connaught Heist case context, and upload a file named `weapon_cv.jpg` (or any image). The system automatically runs classification.
3. **AI Analysis**: Open the AI Evidence Analyzer, select the file, and click **Analyze**. For images, it draws colored bounding boxes indicating weapon detections. For documents, it extracts Named Entity clusters (Person, Weapon, Place).
4. **Download Report**: Go to the Dossier Generator and download the compiled confidential investigation PDF.
5. **Check Chatbot**: Open the Chatbot assistant and click suggested bubbles like "Generate checklist" or ask "how to see maps".

---

## 🛡️ Ethical AI & Cybersecurity Features

- **Chain-of-Custody Logging**: Every time evidence is uploaded or transferred, a cryptographic history is saved (handler ID, action, timestamp) preventing evidence tampering.
- **Audit Trails**: Security actions (failed logins, report downloads, database updates) are committed to a secure file `crimeintel_audit.log` conforming to cybersecurity standards.
- **Explainable AI (XAI)**: Similarity scores and risk percentages show exactly what parameters (e.g. weapon tags, transaction amounts) influenced the recommendation.

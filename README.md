# Elderly & Career Intelligence Hub
### Intelligent Health Telemetry (ByteLife Core) & Skill Gap Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9-orange.svg)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-20%20Passed-success.svg)]()

---

## 1. Project Overview & Architecture
The **Elderly & Career Intelligence Hub** is a dual-domain AI platform engineered to solve two critical real-world challenges:
1. **Real-Time Senior Health Monitoring & Automated Emergency Dispatch (ByteLife Core)**: Continuous physiological telemetry monitoring backed by a dual-layer safety architecture (Machine Learning classifier + Clinical Rule-Based safety override) and automated caretaker notification alerts.
2. **Career & Skill Intelligence Dashboard**: Automated resume text and competency parsing, role benchmark matching, skill gap analysis, and interactive upskilling roadmaps.

```
                          +--------------------------------------------------+
                          |             Senior-Accessible Web UI             |
                          |  - Senior View (Large Fonts & High Contrast)     |
                          |  - Speech Synthesis Readout (Audio Alerts)       |
                          |  - Interactive Chart.js Analytics                |
                          +-------------------------+------------------------+
                                                    |
                                                    | REST APIs (JSON)
                                                    v
+-----------------------------------------------------------------------------------------------+
|                                    Flask Application (app.py)                                 |
|                                                                                               |
|  +--------------------------------------------+   +-----------------------------------------+ |
|  | Module A: ByteLife Health Telemetry Core   |   | Module C: Career & Skill Intelligence   | |
|  | - Random Forest Classifier (99.78% Acc)    |   | - Resume NLP Skill Extractor            | |
|  | - Clinical Rule-Based Failsafe Override    |   | - Role Benchmark Taxonomy Matcher       | |
|  | - Actionable Remedy & OTC Guidance Engine   |   | - Dynamic Gap Analysis & Roadmap        | |
|  +---------------------+----------------------+   +-----------------------------------------+ |
|                        |                                                                      |
|                        v                                                                      |
|  +--------------------------------------------+   +-----------------------------------------+ |
|  | Module B: Caretaker Notification Engine    |   | Local Storage & Model Artifacts         | |
|  | - Secure SMTP Dispatch (TLS / Gmail)       |   | - models/health_model.pkl               | |
|  | - Resilient Local Audit Logger             |   | - data/vitals_history.json              | |
|  |   (data/alerts_log.json)                   |   | - data/alerts_log.json                  | |
|  +--------------------------------------------+   +-----------------------------------------+ |
+-----------------------------------------------------------------------------------------------+
```

---

## 2. Core Modules & Capabilities

### Module A: Real-Time Health Vitals Monitoring (ByteLife Core)
- **Physiological Inputs**: Heart Rate (bpm), Systolic Blood Pressure (mmHg), Diastolic Blood Pressure (mmHg), Oxygen Saturation ($SpO_2$ in %), and Body Temperature (°F).
- **ML Classification**: Multi-class Random Forest model categorizing status into:
  - `0: Normal` (Healthy physiological baseline)
  - `1: Abnormal` (Mild irregularities, low-grade fever, stage 1 hypertension, minor hypoxia)
  - `2: Critical` (Acute emergencies, hypoxemic respiratory failure, hypertensive crisis, shock)
- **Clinical Rule-Based Safety Failsafe**:
  - Independent safety thresholds guarantee high-risk edge cases are immediately promoted to **Critical** (e.g., $SpO_2 < 90\%$, Systolic $\ge 180$, Heart Rate $> 130$ or $< 45$), preventing false negatives.
- **Remedies & First-Aid**:
  - Generates context-aware medical recommendations, positioning protocols (e.g., High Fowler's for low $SpO_2$), and over-the-counter (OTC) medicine guidance.

### Module B: Automated Caretaker Notification System (`send_email.py`)
- Dispatches automated email alerts when status is **Abnormal** or **Critical**.
- Delivers a structured, high-visibility HTML email and plain-text fallback containing:
  - Patient vital breakdown table
  - Timestamp & unique reference ID
  - Safety override reasons
  - Immediate recommended remedies
  - Emergency hotline instructions
- **Resilient Delivery**: If SMTP credentials are missing or the system is offline, it falls back to **Simulated Dispatch Mode**, securely writing records to `data/alerts_log.json` without breaking the user experience.

### Module C: Career & Skill Intelligence Dashboard (`career_intelligence.py`)
- Extracts technical skills, frameworks, and methodologies from free-form text or resumes.
- Benchmarks against 5 core industry role taxonomies:
  - Data Analyst
  - AI & Data Science Architect
  - Healthcare Informatics Specialist
  - Full-Stack AI Engineer
  - Elderly Care & Assistive Tech Specialist
- Generates readiness confidence charts (Chart.js), matched competencies, skill gaps, and prioritized step-by-step upskilling roadmaps.

### Module D: Senior-Friendly Web UX (`templates/index.html`)
- **Senior Accessibility Mode**: Enlarged high-legibility typography, boosted input fields, and simplified contrast.
- **High-Contrast Dark Theme**: Deep black background with high-contrast text for low-vision users.
- **Web Speech API**: Integrated Text-To-Speech (TTS) audio narration for vitals diagnosis and emergency instructions.
- **One-Click Presets**: Simulation buttons for Normal Senior Baseline, Hypertensive Crisis, Hypoxemia, Fever/Tachycardia, and Hypotension.

### Module E: Digital Me (AI Persona & RAG Digital Twin) (`digital_me_engine.py`)
- **First-Person Persona**: Represents **Pranith Kumar Dupuguntla** (Data Analyst & B.Tech CSE Data Science, ACE Engineering College).
- **RAG Knowledge Base**:
  - Ingests `personal_qa.txt`, `resume_summary.txt`, and `projects_research.txt`.
  - Ingests full 41-page ByteLife mini-project report (`bytelife_report.txt`) covering Random Forest model, clinical safety overrides, and vital sign thresholds.
  - Ingests full 8-page peer-reviewed IJIRSET research publication (`microskills_paper.txt`) on AI micro-skill extraction.
- **Vector Store & Embeddings**: Dense vector representations using FastEmbed (`BAAI/bge-small-en-v1.5`) stored in a persistent ChromaDB database (`chroma_digital_me`, 152 semantic chunks).
- **Interactive Web Chat**: Dedicated tab in the web dashboard featuring one-click prompt chips, verified citation badges, and text-to-speech narration.
- **APIs**:
  - `POST /api/digital_me/chat`: Conversational RAG query endpoint.
  - `GET /api/digital_me/suggested`: Prompt recommendations and profile highlights.
  - `POST /api/query`: Backward-compatible legacy query endpoint.

---

## 3. Directory Structure
```
├── app.py                      # Core Flask server and API routing
├── digital_me_engine.py        # Digital Twin semantic RAG engine & persona synthesis
├── build_digital_me_index.py   # Full document & PDF chunking and Chroma vector indexing
├── career_intelligence.py      # Skill extractor, gap analysis, and taxonomy engine
├── train.py                    # Dataset synthesis, model training & export
├── send_email.py               # SMTP notification & resilient fallback engine
├── digital_me .ipynb           # Interactive Jupyter Notebook for Digital Me RAG pipeline
├── verify_live_api.py          # End-to-end verification script for live API
├── test_app_endpoints.py       # Automated test suite for Digital Me endpoints
├── requirements.txt            # Python dependencies
├── implementation_plan.md      # Architecture and design breakdown
├── README.md                   # Complete operational documentation
├── .env.example                # Template for environment variables
├── knowledge_base/             # Ingested knowledge documents (Q&A, resume, ByteLife report, IJIRSET paper)
├── chroma_digital_me/          # Persistent ChromaDB vector database (152 chunks)
├── models/
│   ├── health_model.pkl        # Serialized Random Forest classifier
│   └── model_metrics.json      # Training metrics, report & confusion matrix
├── data/
│   ├── vitals_history.json     # Stored historical vitals records
│   └── alerts_log.json         # Caretaker notifications audit trail
├── static/
│   ├── css/
│   │   └── style.css           # Senior-accessible and high-contrast styling
│   └── js/
│       └── main.js             # Client reactivity, Chart.js, Digital Me & API handlers
├── templates/
│   └── index.html              # Responsive multi-tab dashboard (with Digital Me tab)
└── tests/
    ├── __init__.py
    └── test_health_and_alert.py # Unit & integration tests (pytest)
```

---

## 4. Installation & Setup Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- pip

### Step 1: Clone or Navigate to Directory
```bash
cd "c:\Users\prane\OneDrive\Desktop\digit_me doc"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Train and Serialize the ML Model
```bash
python train.py
```
*Output: Generates 4,500 clinically stratified synthetic patient samples, achieves ~99.8% test accuracy, and exports `models/health_model.pkl`.*

### Step 4: Configure Email Notifications (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` to configure your SMTP provider:
```ini
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_16_digit_app_password
ALERT_SENDER_EMAIL=alerts@bytelife.ai
DEFAULT_CARETAKER_EMAIL=caretaker@bytelife.ai
```
> **Note**: If `.env` credentials are not supplied, the platform automatically runs in **Simulated Dispatch Mode**, writing every notification to `data/alerts_log.json` for auditing.

---

## 5. Running the Application

### Start the Flask Server
```bash
python app.py
```
The server will initialize on:
**`http://127.0.0.1:5000`**

Open this URL in any modern browser to access the interactive dashboard.

---

## 6. Testing & Validation

### Run the Pytest Unit Test Suite
```bash
pytest tests/test_health_and_alert.py -v
```
All **19 test cases** validate:
- Model serialization and loading
- Classification of normal and critical vitals
- Clinical rule-based failsafe activations
- Remedy and first-aid recommendations
- Email alert dispatch and file auditing
- NLP skill extraction and career gap calculations
- Flask REST endpoints (`/health`, `/api/predict-health`, `/api/analyze-skills`, `/api/vitals-history`)

### Run Live End-to-End API Verification
With the server running, execute:
```bash
python verify_live_api.py
```

---

## 7. REST API Reference

### 1. Health Telemetry Evaluation
- **Endpoint**: `POST /api/predict-health`
- **Request Body**:
  ```json
  {
    "patient_name": "Senior Resident",
    "heart_rate": 136,
    "systolic_bp": 188,
    "diastolic_bp": 122,
    "spo2": 87.5,
    "temperature": 102.8,
    "recipient_email": "caretaker@bytelife.ai",
    "auto_alert": true
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "status_code": 2,
    "status_label": "Critical",
    "ml_predicted_class": 2,
    "ml_confidence_percentage": 99.1,
    "rule_override": false,
    "remedies": [
      {
        "title": "Emergency Dispatch",
        "category": "Immediate Medical Action",
        "description": "Alert emergency response services (911/112).",
        "urgent": true
      }
    ],
    "alert_info": {
      "success": true,
      "mode": "simulated_dispatch",
      "message_id": "ALERT-A80AB101"
    }
  }
  ```

### 2. Career & Skill Intelligence
- **Endpoint**: `POST /api/analyze-skills`
- **Request Body**:
  ```json
  {
    "resume_text": "Power BI, DAX, Python, Pandas, SQL, Excel, Healthcare Analytics",
    "target_role": "Data Analyst"
  }
  ```
- **Response**:
  ```json
  {
    "target_role": "Data Analyst",
    "target_evaluation": {
      "match_percentage": 77.8,
      "matched_skills": ["python", "pandas", "power bi", "dax", "microsoft excel", "sql"],
      "missing_skills": ["data visualization", "kpi reporting", "dashboard development"]
    },
    "upskilling_roadmap": [
      {
        "skill": "Data Visualization",
        "priority": "High Priority (Next 30 Days)",
        "action": "Complete hands-on project and validation labs for Data Visualization."
      }
    ]
  }
  ```

---

## 8. Clinical Vital Thresholds Reference

| Metric | Normal Range (0) | Abnormal / Caution (1) | Critical Emergency (2) |
| :--- | :--- | :--- | :--- |
| **Heart Rate** | 60 – 100 bpm | 50–59 bpm or 101–130 bpm | $< 45\text{ bpm}$ or $> 130\text{ bpm}$ |
| **Systolic BP** | 90 – 120 mmHg | 125–179 mmHg or 85–89 mmHg | $\ge 180\text{ mmHg}$ or $< 85\text{ mmHg}$ |
| **Diastolic BP** | 60 – 80 mmHg | 82–119 mmHg or 50–59 mmHg | $\ge 120\text{ mmHg}$ or $< 50\text{ mmHg}$ |
| **SpO2 Oxygen** | 95% – 100% | 90% – 94.9% | $< 90\%$ (Severe Hypoxemia) |
| **Temperature** | 97.0°F – 99.0°F | 99.1°F – 102.9°F or 95.0°F–96.9°F | $\ge 103.0^\circ\text{F}$ or $< 95.0^\circ\text{F}$ |

---

## 9. Contributors & License
Developed as part of the **ByteLife Core & Digital Me** intelligent systems architecture.
Licensed under the MIT License.

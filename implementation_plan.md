# Implementation Plan: Elderly & Career Intelligence Hub

## 1. System Overview & Architecture
The **Elderly & Career Intelligence Hub** is an integrated, dual-purpose intelligent web application built using Python (Flask) on the backend and modern, senior-accessible HTML5/CSS3/JavaScript on the frontend. The platform serves two high-value domains:
1. **ByteLife Core (Health Monitoring & Alerting)**: Real-time physiological vitals monitoring with dual-layer safety (Machine Learning Classifier + Rule-Based Clinical Failsafe) and automated caretaker notifications.
2. **Career & Skill Intelligence Hub**: Automated resume and skill profile parsing, skill gap analysis, confidence scoring, and interactive visual career roadmaps.

```
                      +------------------------------------------+
                      |         Accessible Web Dashboard         |
                      |   (Senior-Friendly / Caretaker / Admin)  |
                      +--------------------+---------------------+
                                           | HTTP / JSON REST APIs
                                           v
+-----------------------------------------------------------------------------------+
|                            Flask Backend (app.py)                                 |
|                                                                                   |
|  +------------------------------+     +-----------------------------------------+ |
|  |   Module A: ByteLife Core    |     | Module C: Career & Skill Intelligence   | |
|  | - ML Classifier (PKL Model)  |     | - Resume & Skill Text Parser            | |
|  | - Rule-Based Backup Safety   |     | - Role Benchmark Matcher (TF-IDF/Rules) | |
|  | - Clinical Remedy Engine     |     | - Skill Gap & Roadmap Generator         | |
|  +--------------+---------------+     +-----------------------------------------+ |
|                 |                                                                 |
|                 v                                                                 |
|  +------------------------------+     +-----------------------------------------+ |
|  | Module B: Caretaker Alerts   |     | Local Storage Engine                    | |
|  | - Secure SMTP Dispatcher     |     | - models/health_model.pkl               | |
|  | - JSON Fallback Alert Logger |     | - data/vitals_history.json              | |
|  +------------------------------+     +-----------------------------------------+ |
+-----------------------------------------------------------------------------------+
```

---

## 2. Component Breakdown

### Module A: Real-Time Health Vitals Monitoring (ByteLife Core)
- **Inputs**:
  - Heart Rate ($HR$ in bpm)
  - Blood Pressure ($BP_{sys}$ and $BP_{dia}$ in mmHg)
  - Oxygen Saturation ($SpO_2$ in %)
  - Body Temperature ($Temp$ in °F)
- **Machine Learning Model**:
  - Algorithm: Random Forest Classifier trained on clinically correlated physiological data.
  - Multi-class output:
    - `0`: Normal (Healthy stable vitals)
    - `1`: Abnormal (Requiring observation, lifestyle adjustment, or non-acute OTC remedies)
    - `2`: Critical (Acute emergency requiring immediate intervention and caretaker alert)
  - Serialized to `models/health_model.pkl` with metadata and feature scaling.
- **Rule-Based Safety Override (Failsafe Mechanism)**:
  - Clinical safety thresholds operate alongside the ML model. If an acute physiological anomaly occurs (e.g., $SpO_2 < 90\%$, Systolic $\ge 180$, Heart Rate $> 140$ or $< 45$, Temperature $\ge 103^\circ\text{F}$), the classification is immediately promoted to **Critical**, logging a safety override reason.
- **Clinical Remedy Recommendation Engine**:
  - Contextual remedies and first-aid recommendations mapped directly to abnormal vitals (e.g., oxygen therapy positioning, hydration protocols, OTC antipyretics, hypertensive rest guidelines).

### Module B: Caretaker Notification System (`send_email.py`)
- **Triggers**: Automatically dispatched when health classification is `Abnormal` or `Critical`.
- **Email Contents**:
  - Patient status badge (Abnormal / Critical)
  - Formatted vitals table with deviation flags
  - Timestamp of measurement
  - Immediate recommended remedies & OTC guidance
  - Urgent emergency notice for Critical vitals
- **Security & Reliability**:
  - TLS/SSL secure SMTP via environment variables (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`).
  - Graceful fallback: If credentials are not supplied or the network is isolated, the alert payload is saved to `data/alerts_log.json` and logged to console, maintaining uninterrupted UI operation.

### Module C: Career & Skill Intelligence Dashboard
- **Parser & Skill Extractor**:
  - Analyzes resume text, project summaries, or technical skill entries against a comprehensive tech & healthcare taxonomy.
- **Role Benchmarking**:
  - Evaluates match scores against target profiles: Data Analyst, Senior AI/ML Engineer, Healthcare Informatics Specialist, Full-Stack Developer, and Technical Project Manager.
- **Gap Analysis & Recommendations**:
  - Outputs matched competencies, missing prerequisites, prioritized upskilling roadmap, and readiness confidence index.
- **Visual Analytics**:
  - Generates radar and bar chart datasets rendered with Chart.js on the frontend.

### Module D: Frontend UI & Senior-Friendly UX
- Accessible design adhering to WCAG guidelines:
  - Contrast toggle (Standard Light, Modern Dark, High-Contrast Senior Mode)
  - Adjustable font scale (Normal, Large, Extra Large)
  - Visual status banners with pulse indicators
  - Audio alert announcement (Web Speech API integration)
  - One-click presets: "Normal Senior", "Hypertensive Crisis", "Acute Hypoxemia", "Fever/Tachycardia"
  - Interactive charts for vitals progression and skill match distribution.

---

## 3. Directory & File Structure
```
elderly_career_hub/
├── app.py                      # Core Flask application, API routes, and view controllers
├── train.py                    # Dataset generator, model training, validation, and serialization
├── send_email.py               # SMTP and fallback alert notification engine
├── requirements.txt            # Dependency definitions
├── implementation_plan.md      # Architecture and design specification
├── README.md                   # Operational manual, environment configuration, and test guide
├── models/
│   └── health_model.pkl        # Trained Random Forest classifier + metadata
├── data/
│   ├── vitals_history.json     # Saved vitals logs
│   └── alerts_log.json         # Caretaker notifications audit log
├── static/
│   ├── css/
│   │   └── style.css           # Senior-accessible responsive styles
│   └── js/
│       └── main.js             # Client-side reactivity, chart rendering, API handlers
├── templates/
│   └── index.html              # Comprehensive dashboard UI
└── tests/
    ├── __init__.py
    └── test_health_and_alert.py # Pytest test suite covering ML, safety rules, email, & APIs
```

---

## 4. Execution Steps
1. **Dependencies Installation**: Install `scikit-learn`, `pandas`, `joblib`, `pytest`, `python-dotenv`, `flask`, `flask-cors`.
2. **Model Training & Serialization**: Run `train.py` to synthesize clinically aligned training data, train a Random Forest model, assess test accuracy/F1-score, and export `models/health_model.pkl`.
3. **Core Utility & Backend Development**: Implement `send_email.py` and `app.py` with all required endpoints:
   - `POST /api/predict-health`
   - `POST /api/send-alert`
   - `POST /api/analyze-skills`
   - `GET /api/vitals-history`
   - `GET /api/system-status`
4. **Senior-Friendly Frontend Implementation**: Develop `templates/index.html`, `static/css/style.css`, and `static/js/main.js`.
5. **Testing & Validation**:
   - Run `pytest` on `tests/test_health_and_alert.py`.
   - Start Flask server on port 5000 and execute automated HTTP requests testing Normal, Abnormal, and Critical submissions.
6. **Documentation**: Finalize README.md with comprehensive guides for local execution and caretaker alerting.

"""
app.py - Main Flask Application for Elderly & Career Intelligence Hub
Integrates:
- Module A: Real-Time Health Vitals Monitoring (ByteLife Core) with ML + Rule-Based Safety Failsafe
- Module B: Automated Caretaker Notification System (Secure SMTP & Resilient Audit Log)
- Module C: Career & Skill Intelligence Dashboard (Resume Parser, Gap Analysis & Roadmap)
- Module D: Senior-Friendly Accessible Web Interface
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from send_email import send_caretaker_alert, get_alert_history
from career_intelligence import analyze_career_skills, ROLE_TAXONOMY

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
if not os.path.exists(TEMPLATES_DIR):
    TEMPLATES_DIR = os.path.join(BASE_DIR, "static", "templates")

app = Flask(__name__, template_folder=TEMPLATES_DIR)
CORS(app)

# Configuration & Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "health_model.pkl")
DATA_DIR = os.path.join(BASE_DIR, "data")
VITALS_HISTORY_PATH = os.path.join(DATA_DIR, "vitals_history.json")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Global Model Cache
HEALTH_MODEL_BUNDLE = None

def load_health_model():
    """Load or train the health classification model."""
    global HEALTH_MODEL_BUNDLE
    if os.path.exists(MODEL_PATH):
        try:
            HEALTH_MODEL_BUNDLE = joblib.load(MODEL_PATH)
            print(f"[*] Successfully loaded Health Model from {MODEL_PATH}")
            return HEALTH_MODEL_BUNDLE
        except Exception as e:
            print(f"[!] Warning: Failed to load existing model: {e}")

    # Fallback to training a fresh model if missing
    try:
        from train import train_health_model
        print("[*] Training fresh model...")
        HEALTH_MODEL_BUNDLE = train_health_model()
        return HEALTH_MODEL_BUNDLE
    except Exception as e:
        print(f"[!] Error training fallback model: {e}")
        return None

# Load model on startup
load_health_model()


def evaluate_clinical_rules(heart_rate, systolic_bp, diastolic_bp, spo2, temperature):
    """
    Rule-Based Safety Failsafe Engine.
    Evaluates acute physiological thresholds independently of the ML model
    to prevent false negatives for high-risk critical anomalies.
    Returns: (is_critical, is_abnormal, list_of_reasons)
    """
    critical_flags = []
    abnormal_flags = []

    # 1. Oxygen Saturation (SpO2)
    if spo2 < 90.0:
        critical_flags.append(f"SpO2 critically low at {spo2}% (Severe Hypoxemia < 90%)")
    elif spo2 < 95.0:
        abnormal_flags.append(f"SpO2 sub-optimal at {spo2}% (Mild Hypoxemia 90-94%)")

    # 2. Blood Pressure (Systolic & Diastolic)
    if systolic_bp >= 180.0 or diastolic_bp >= 120.0:
        critical_flags.append(f"Blood Pressure indicates Hypertensive Crisis: {systolic_bp}/{diastolic_bp} mmHg (Sys >= 180 or Dia >= 120)")
    elif systolic_bp < 85.0 or diastolic_bp < 50.0:
        critical_flags.append(f"Blood Pressure indicates Circulatory Shock / Severe Hypotension: {systolic_bp}/{diastolic_bp} mmHg")
    elif systolic_bp >= 125.0 or diastolic_bp >= 82.0:
        abnormal_flags.append(f"Blood Pressure elevated: {systolic_bp}/{diastolic_bp} mmHg (Stage 1/2 Hypertension)")
    elif systolic_bp < 90.0 or diastolic_bp < 60.0:
        abnormal_flags.append(f"Blood Pressure mildly low: {systolic_bp}/{diastolic_bp} mmHg")

    # 3. Heart Rate (Pulse)
    if heart_rate > 130.0:
        critical_flags.append(f"Heart Rate critically high: {heart_rate} bpm (Severe Tachycardia > 130 bpm)")
    elif heart_rate < 45.0:
        critical_flags.append(f"Heart Rate critically low: {heart_rate} bpm (Severe Bradycardia < 45 bpm)")
    elif heart_rate > 100.0:
        abnormal_flags.append(f"Heart Rate elevated: {heart_rate} bpm (Mild Tachycardia 101-130 bpm)")
    elif heart_rate < 60.0:
        abnormal_flags.append(f"Heart Rate low: {heart_rate} bpm (Mild Bradycardia 45-59 bpm)")

    # 4. Body Temperature
    if temperature >= 103.0:
        critical_flags.append(f"Body Temperature critically high: {temperature}°F (Hyperpyrexia >= 103°F)")
    elif temperature < 95.0:
        critical_flags.append(f"Body Temperature critically low: {temperature}°F (Hypothermia < 95°F)")
    elif temperature > 99.0:
        abnormal_flags.append(f"Body Temperature elevated: {temperature}°F (Low/Moderate Fever)")
    elif temperature < 97.0:
        abnormal_flags.append(f"Body Temperature slightly low: {temperature}°F")

    is_critical = len(critical_flags) > 0
    is_abnormal = len(abnormal_flags) > 0

    return is_critical, is_abnormal, critical_flags + abnormal_flags


def generate_remedies_and_actions(vitals, status_label):
    """
    Generates actionable clinical guidance, first-aid measures,
    and over-the-counter (OTC) medicine recommendations based on patient vitals.
    """
    remedies = []
    hr = vitals.get("heart_rate", 75)
    sys = vitals.get("systolic_bp", 120)
    dia = vitals.get("diastolic_bp", 80)
    spo2 = vitals.get("spo2", 98)
    temp = vitals.get("temperature", 98.6)

    if status_label == "Critical":
        remedies.append({
            "title": "Emergency Dispatch",
            "category": "Immediate Medical Action",
            "description": "Alert emergency response services (911/112). Patient requires prompt hospital/clinical triage.",
            "urgent": True
        })
        if spo2 < 90.0:
            remedies.append({
                "title": "High Fowler's Positioning & Oxygen Support",
                "category": "Respiratory First-Aid",
                "description": "Sit the patient fully upright (75-90 degrees) to maximize lung volume. Administer supplemental oxygen if prescribed equipment is on site.",
                "urgent": True
            })
        if sys >= 180.0 or dia >= 120.0:
            remedies.append({
                "title": "Hypertensive Urgency Management",
                "category": "Cardiovascular Protocol",
                "description": "Keep the patient calm and resting in a quiet, low-stimulus environment. Do not administer acute unprescribed anti-hypertensive drugs without physician direct order.",
                "urgent": True
            })
        if hr > 130.0 or hr < 45.0:
            remedies.append({
                "title": "Arrhythmia Precaution",
                "category": "Cardiac Protocol",
                "description": "Have patient remain supine or seated. Avoid sudden postural shifts to prevent fainting (syncope) and check carotid/radial pulse.",
                "urgent": True
            })
        if temp >= 103.0:
            remedies.append({
                "title": "Active Cooling & Hydration",
                "category": "Hyperpyrexia Protocol",
                "description": "Apply cool, damp washcloths to forehead, axillae, and neck. Offer electrolyte fluids if conscious and prepare antipyretic administration.",
                "urgent": True
            })

    elif status_label == "Abnormal":
        remedies.append({
            "title": "Rest & Vital Trend Monitoring",
            "category": "Observation Protocol",
            "description": "Patient should sit in a supportive armchair and avoid physical exertion. Re-evaluate vitals in 20 minutes.",
            "urgent": False
        })
        if spo2 < 95.0:
            remedies.append({
                "title": "Pursed-Lip Deep Breathing",
                "category": "Respiratory Care",
                "description": "Instruct patient to breathe in slowly through the nose for 2 seconds and exhale through pursed lips for 4 seconds. Ensure room has adequate airflow.",
                "urgent": False
            })
        if sys >= 125.0 or dia >= 82.0:
            remedies.append({
                "title": "Blood Pressure Calming & Hydration",
                "category": "Cardiovascular Care",
                "description": "Hydrate with a glass of water. Practice 5 minutes of guided slow breathing. Avoid sodium snacks, coffee, tea, and tobacco.",
                "urgent": False
            })
        if temp > 99.0:
            remedies.append({
                "title": "Hydration & OTC Antipyretic",
                "category": "Fever Management",
                "description": "Provide lukewarm fluids (water, broth, herbal tea). Under healthcare provider guidance, consider OTC Acetaminophen (Paracetamol) 500mg or Ibuprofen 200mg.",
                "urgent": False
            })
        if hr > 100.0 or hr < 60.0:
            remedies.append({
                "title": "Heart Rate Stabilization",
                "category": "Pulse Care",
                "description": "Slowly drink cool water. Check if recent caffeine, decongestants, or missed medications contributed to pulse fluctuation.",
                "urgent": False
            })

    else:
        # Normal
        remedies.append({
            "title": "Normal Baseline Maintenance",
            "category": "Wellness",
            "description": "All monitored vitals are within healthy physiological limits. Maintain regular hydration, balanced nutrition, and daily light physical activity.",
            "urgent": False
        })
        remedies.append({
            "title": "Routine Schedule",
            "category": "Preventive Care",
            "description": "Next scheduled vitals check recommended in 12 to 24 hours.",
            "urgent": False
        })

    return remedies


def save_vitals_record(record):
    """Append vitals record to historical JSON database."""
    history = []
    if os.path.exists(VITALS_HISTORY_PATH):
        try:
            with open(VITALS_HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.insert(0, record)
    history = history[:100]  # Store last 100 checks
    with open(VITALS_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def get_vitals_history():
    """Retrieve vitals assessment history."""
    if os.path.exists(VITALS_HISTORY_PATH):
        try:
            with open(VITALS_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


# ==========================================================
# Flask Routes & Endpoints
# ==========================================================

@app.route("/", methods=["GET"])
def index():
    """Renders the comprehensive user and caretaker dashboard."""
    return render_template("index.html")


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health_status():
    """Health status endpoint verifying backend and ML model readiness."""
    model_loaded = HEALTH_MODEL_BUNDLE is not None
    model_accuracy = HEALTH_MODEL_BUNDLE.get("accuracy", 0.0) if model_loaded else 0.0
    return jsonify({
        "status": "healthy",
        "service": "Elderly & Career Intelligence Hub Backend",
        "model_loaded": model_loaded,
        "model_accuracy": f"{model_accuracy * 100:.2f}%" if model_loaded else "N/A",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route("/api/predict-health", methods=["POST"])
def predict_health():
    """
    Primary endpoint for Real-Time Health Vitals Monitoring (ByteLife Core).
    Evaluates physiological inputs with ML + Rule-Based safety override.
    Dispatches automated caretaker notification on Abnormal or Critical status.
    """
    data = request.get_json() or {}
    
    # 1. Input Extraction & Validation
    patient_name = data.get("patient_name", "Senior Patient").strip() or "Senior Patient"
    recipient_email = data.get("recipient_email", "").strip()
    auto_alert = data.get("auto_alert", True)

    try:
        hr = float(data.get("heart_rate"))
        sys_bp = float(data.get("systolic_bp"))
        dia_bp = float(data.get("diastolic_bp"))
        spo2 = float(data.get("spo2"))
        temp = float(data.get("temperature"))
    except (TypeError, ValueError):
        return jsonify({
            "error": "Invalid or missing vital metrics. Ensure Heart Rate, Blood Pressure (Sys & Dia), SpO2, and Body Temperature are numeric values."
        }), 400

    # Bounds validation (prevent physiologically absurd values)
    if not (25 <= hr <= 250):
        return jsonify({"error": f"Heart rate of {hr} bpm is outside physiological bounds (25-250 bpm)."}), 400
    if not (40 <= sys_bp <= 300) or not (20 <= dia_bp <= 200):
        return jsonify({"error": f"Blood pressure {sys_bp}/{dia_bp} mmHg is outside valid ranges (Sys 40-300, Dia 20-200)."}), 400
    if not (50.0 <= spo2 <= 100.0):
        return jsonify({"error": f"SpO2 of {spo2}% is outside valid oxygen saturation range (50-100%)."}), 400
    if not (85.0 <= temp <= 115.0):
        return jsonify({"error": f"Body temperature of {temp}°F is outside valid medical range (85-115°F)."}), 400

    vitals = {
        "heart_rate": round(hr, 1),
        "systolic_bp": round(sys_bp, 1),
        "diastolic_bp": round(dia_bp, 1),
        "spo2": round(spo2, 1),
        "temperature": round(temp, 1)
    }

    # 2. Machine Learning Prediction
    ml_class = 0
    ml_confidence = 0.95
    probabilities = {"Normal": 0.95, "Abnormal": 0.04, "Critical": 0.01}

    if HEALTH_MODEL_BUNDLE is not None:
        model = HEALTH_MODEL_BUNDLE["model"]
        feature_names = HEALTH_MODEL_BUNDLE.get("feature_names", ["heart_rate", "systolic_bp", "diastolic_bp", "spo2", "temperature"])
        input_df = pd.DataFrame([[hr, sys_bp, dia_bp, spo2, temp]], columns=feature_names)
        ml_pred = model.predict(input_df)[0]
        ml_class = int(ml_pred)

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(input_df)[0]
            ml_confidence = float(np.max(probs))
            classes = [HEALTH_MODEL_BUNDLE["class_mapping"][c] for c in model.classes_]
            probabilities = {cls: round(float(prob), 4) for cls, prob in zip(classes, probs)}
    else:
        # Fallback simple threshold if model failed to load
        if spo2 < 90 or sys_bp >= 180 or hr > 130:
            ml_class = 2
        elif spo2 < 95 or sys_bp >= 130 or hr > 100:
            ml_class = 1
        else:
            ml_class = 0

    # 3. Rule-Based Safety Failsafe
    is_crit_rule, is_abnorm_rule, rule_reasons = evaluate_clinical_rules(hr, sys_bp, dia_bp, spo2, temp)
    
    rule_override = False
    override_reason = None
    final_status_code = ml_class

    if is_crit_rule and ml_class < 2:
        final_status_code = 2
        rule_override = True
        override_reason = f"Safety Rule Failsafe: Promoted to CRITICAL due to: {'; '.join(rule_reasons)}"
    elif is_abnorm_rule and ml_class == 0:
        final_status_code = 1
        rule_override = True
        override_reason = f"Safety Rule Failsafe: Promoted to ABNORMAL due to: {'; '.join(rule_reasons)}"

    status_labels = {0: "Normal", 1: "Abnormal", 2: "Critical"}
    final_status_label = status_labels[final_status_code]

    # 4. Remedy Recommendations
    remedies = generate_remedies_and_actions(vitals, final_status_label)

    # 5. Automated Caretaker Notification
    alert_result = None
    if auto_alert and final_status_code in [1, 2]:
        alert_result = send_caretaker_alert(
            patient_name=patient_name,
            vitals=vitals,
            alert_level=final_status_label,
            recipient_email=recipient_email,
            remedies=remedies,
            rule_overrides=rule_reasons if rule_override else None,
            override_reason=override_reason
        )

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 6. Save Assessment Record
    record = {
        "timestamp": timestamp_str,
        "patient_name": patient_name,
        "vitals": vitals,
        "status_code": final_status_code,
        "status_label": final_status_label,
        "confidence": round(ml_confidence * 100, 1),
        "rule_override": rule_override,
        "override_reason": override_reason,
        "alert_dispatched": alert_result is not None,
        "alert_mode": alert_result.get("mode") if alert_result else None
    }
    save_vitals_record(record)

    return jsonify({
        "success": True,
        "patient_name": patient_name,
        "timestamp": timestamp_str,
        "vitals": vitals,
        "status_code": final_status_code,
        "status_label": final_status_label,
        "ml_predicted_class": ml_class,
        "ml_predicted_label": status_labels[ml_class],
        "ml_confidence_percentage": round(ml_confidence * 100, 1),
        "probabilities": probabilities,
        "rule_override": rule_override,
        "override_reason": override_reason,
        "remedies": remedies,
        "alert_info": alert_result
    }), 200


@app.route("/api/send-alert", methods=["POST"])
def manual_send_alert():
    """Manual caretaker notification dispatch endpoint."""
    data = request.get_json() or {}
    patient_name = data.get("patient_name", "Senior Patient")
    recipient_email = data.get("recipient_email", "")
    alert_level = data.get("alert_level", "Abnormal")
    vitals = data.get("vitals", {})
    remedies = data.get("remedies", [])

    if not remedies:
        remedies = generate_remedies_and_actions(vitals, alert_level)

    res = send_caretaker_alert(
        patient_name=patient_name,
        vitals=vitals,
        alert_level=alert_level,
        recipient_email=recipient_email,
        remedies=remedies
    )
    return jsonify(res), 200


@app.route("/api/vitals-history", methods=["GET"])
def vitals_history():
    """Returns stored vitals history."""
    history = get_vitals_history()
    return jsonify({
        "count": len(history),
        "history": history
    }), 200


@app.route("/api/alerts-history", methods=["GET"])
def alerts_history():
    """Returns stored caretaker alerts audit trail."""
    history = get_alert_history()
    return jsonify({
        "count": len(history),
        "alerts": history
    }), 200


@app.route("/api/analyze-skills", methods=["POST"])
def analyze_skills():
    """
    Module C: Career & Skill Intelligence Dashboard API.
    Parses resume text or custom skill entries, performs role benchmark matching,
    calculates skill gaps, and returns confidence metrics for visual charts.
    """
    data = request.get_json() or {}
    resume_text = data.get("resume_text", "")
    target_role = data.get("target_role", "Data Analyst")

    if not resume_text or len(resume_text.strip()) < 5:
        # Load local resume summary as a default sample if text is empty
        summary_path = os.path.join(BASE_DIR, "resume_summary.txt")
        if os.path.exists(summary_path):
            with open(summary_path, "r", encoding="utf-8") as f:
                resume_text = f.read()
        else:
            resume_text = "Python, SQL, Pandas, NumPy, Power BI, Excel, Data Analysis"

    analysis = analyze_career_skills(resume_text, target_role=target_role)
    return jsonify(analysis), 200


@app.route("/api/skill-roles", methods=["GET"])
def skill_roles():
    """Returns available benchmark career roles."""
    roles = []
    for name, info in ROLE_TAXONOMY.items():
        roles.append({
            "name": name,
            "category": info["category"],
            "description": info["description"],
            "skill_count": len(info["skills"]),
            "skills_preview": info["skills"][:6]
        })
    return jsonify({"roles": roles}), 200


# =====================================================================
# DIGITAL ME (AI DIGITAL TWIN) ENDPOINTS
# =====================================================================
try:
    from digital_me_engine import (
        ask_digital_me,
        SUGGESTED_PROMPTS,
        get_current_profile,
        save_person_profile,
        list_all_profiles
    )
    DIGITAL_ME_AVAILABLE = True
except Exception as e:
    print(f"[!] Warning: digital_me_engine failed to load: {e}")
    DIGITAL_ME_AVAILABLE = False
    SUGGESTED_PROMPTS = [
        "Tell me about your ByteLife project",
        "What are your Power BI & DAX skills?",
        "Where did you publish your research?"
    ]
    def get_current_profile():
        return {"name": "Pranith Kumar Dupuguntla", "role": "Data Analyst"}
    def save_person_profile(p):
        return p
    def list_all_profiles():
        return [{"id": "default", "name": "Pranith Kumar Dupuguntla", "role": "Data Analyst"}]

@app.route("/api/profile", methods=["GET"])
def get_profile_endpoint():
    """Retrieve the currently active person profile."""
    return jsonify(get_current_profile()), 200

@app.route("/api/profile", methods=["POST"])
def save_profile_endpoint():
    """Create or update a person profile."""
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"error": "Profile 'name' is required"}), 400
    saved = save_person_profile(data)
    return jsonify({"message": "Profile saved successfully", "profile": saved}), 200

@app.route("/api/profiles", methods=["GET"])
def list_profiles_endpoint():
    """List all available person profiles."""
    return jsonify({"profiles": list_all_profiles()}), 200

@app.route("/api/profile/switch", methods=["POST"])
def switch_profile_endpoint():
    """Switch active person profile by ID."""
    data = request.get_json() or {}
    pid = data.get("id")
    prof_file = os.path.join(DATA_DIR, "profiles", f"{pid}.json")
    if os.path.exists(prof_file):
        with open(prof_file, "r", encoding="utf-8") as f:
            pdata = json.load(f)
        with open(os.path.join(DATA_DIR, "current_profile.json"), "w", encoding="utf-8") as f:
            json.dump(pdata, f, indent=2)
        return jsonify({"message": f"Switched to profile: {pdata.get('name')}", "profile": pdata}), 200
    return jsonify({"error": f"Profile with id '{pid}' not found"}), 404

@app.route("/api/digital_me/chat", methods=["POST"])
def digital_me_chat():
    """Interactive First-Person Digital Twin Chat Endpoint."""
    data = request.get_json() or {}
    user_query = data.get("query", "").strip()
    if not user_query:
        return jsonify({"error": "Missing 'query' field in request body"}), 400

    if DIGITAL_ME_AVAILABLE:
        try:
            result = ask_digital_me(user_query)
            return jsonify(result), 200
        except Exception as e:
            print(f"[!] Error in ask_digital_me: {e}")

    # Fallback response if engine error occurs
    return jsonify({
        "query": user_query,
        "response": (
            "Hi, I'm **Pranith Kumar Dupuguntla**! I specialize in Data Analytics, Power BI, Python, and SQL. "
            "I co-authored the **ByteLife health monitoring system** and published research in **IJIRSET** "
            "on AI micro-skill extraction. Feel free to ask more or reach me at Praneeth.dupukuntla@gmail.com!"
        ),
        "sources": [{"title": "Knowledge Base", "source": "local", "snippet": "Pranith Kumar Dupuguntla Data Analyst profile"}],
        "suggested_questions": SUGGESTED_PROMPTS[:3]
    }), 200

@app.route("/api/digital_me/suggested", methods=["GET"])
def digital_me_suggested():
    """Returns profile highlights and suggested prompts for Digital Twin."""
    return jsonify({
        "name": "Pranith Kumar Dupuguntla",
        "role": "Data Analyst & B.Tech CSE (Data Science)",
        "location": "Hyderabad, India",
        "email": "Praneeth.dupukuntla@gmail.com",
        "phone": "+91 6300905921",
        "suggested_questions": SUGGESTED_PROMPTS
    }), 200

# Preserved Digital Twin semantic search endpoint (with fallback if vectorstore is not active)
@app.route("/api/query", methods=["POST"])
def query_digital_twin():
    """Digital Twin semantic query endpoint (backward compatibility)."""
    data = request.get_json() or {}
    user_query = data.get("query", "")
    if not user_query:
        return jsonify({"error": "Missing 'query' field"}), 400

    if DIGITAL_ME_AVAILABLE:
        try:
            result = ask_digital_me(user_query)
            return jsonify({
                "query": user_query,
                "response": result.get("response", ""),
                "results_count": len(result.get("sources", [])),
                "results": result.get("sources", [])
            }), 200
        except Exception as e:
            pass

    # Search in local text files as fallback
    matched_chunks = []
    for txt_file in ["resume_summary.txt", "personal_qa.txt", "projects_research.txt"]:
        file_path = os.path.join(BASE_DIR, txt_file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if any(word.lower() in content.lower() for word in user_query.split() if len(word) > 3):
                    matched_chunks.append({
                        "content": content[:400] + "...",
                        "source": txt_file
                    })

    return jsonify({
        "query": user_query,
        "results_count": len(matched_chunks),
        "results": matched_chunks
    }), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"[*] Starting Elderly & Career Intelligence Hub on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
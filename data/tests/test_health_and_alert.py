"""
test_health_and_alert.py - Pytest Test Suite
Validates:
1. Machine Learning Health Model loading and inference.
2. Clinical Rule-Based Safety Failsafe triggers.
3. Input validation and boundary error handling.
4. Automated Caretaker Notification dispatch and audit logging.
5. Career & Skill Intelligence parsing, role matching, and gap analysis.
6. Flask REST API endpoints integration.
"""

import os
import json
import pytest
import numpy as np
from app import app, load_health_model, evaluate_clinical_rules, generate_remedies_and_actions
from send_email import send_caretaker_alert, get_alert_history
from career_intelligence import extract_skills_from_text, analyze_career_skills, ROLE_TAXONOMY


@pytest.fixture
def client():
    """Flask test client fixture."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ==========================================================
# 1. Machine Learning Model Inference Tests
# ==========================================================
def test_health_model_loading():
    """Verify that the serialized ML model loads properly and contains expected metadata."""
    bundle = load_health_model()
    assert bundle is not None, "Health model bundle failed to load"
    assert "model" in bundle
    assert "accuracy" in bundle
    assert bundle["accuracy"] >= 0.90, f"Expected model accuracy >= 90%, got {bundle['accuracy']}"
    assert "class_mapping" in bundle
    assert bundle["class_mapping"][0] == "Normal"
    assert bundle["class_mapping"][1] == "Abnormal"
    assert bundle["class_mapping"][2] == "Critical"


def test_model_predict_normal_vitals():
    """Verify normal vital readings are classified as Normal (0)."""
    import pandas as pd
    bundle = load_health_model()
    model = bundle["model"]
    feature_names = bundle["feature_names"]
    # HR: 72, Sys: 114, Dia: 74, SpO2: 98.5, Temp: 98.2
    features = pd.DataFrame([[72, 114, 74, 98.5, 98.2]], columns=feature_names)
    pred = model.predict(features)[0]
    assert int(pred) == 0, f"Expected class 0 (Normal), got {pred}"


def test_model_predict_critical_vitals():
    """Verify acute anomalies are classified as Critical (2)."""
    import pandas as pd
    bundle = load_health_model()
    model = bundle["model"]
    feature_names = bundle["feature_names"]
    # Severe hypoxemia: SpO2 = 82%
    features = pd.DataFrame([[125, 110, 70, 82.0, 98.6]], columns=feature_names)
    pred = model.predict(features)[0]
    assert int(pred) == 2, f"Expected class 2 (Critical), got {pred}"


# ==========================================================
# 2. Rule-Based Safety Failsafe Engine Tests
# ==========================================================
def test_clinical_rule_critical_hypoxia():
    """Test that SpO2 < 90% triggers critical failsafe."""
    is_crit, is_abnorm, reasons = evaluate_clinical_rules(
        heart_rate=75, systolic_bp=118, diastolic_bp=76, spo2=87.5, temperature=98.4
    )
    assert is_crit is True
    assert any("SpO2 critically low" in r for r in reasons)


def test_clinical_rule_hypertensive_crisis():
    """Test that Systolic >= 180 or Diastolic >= 120 triggers critical failsafe."""
    is_crit, is_abnorm, reasons = evaluate_clinical_rules(
        heart_rate=88, systolic_bp=188, diastolic_bp=122, spo2=97.0, temperature=98.6
    )
    assert is_crit is True
    assert any("Hypertensive Crisis" in r for r in reasons)


def test_clinical_rule_abnormal_prehypertension():
    """Test that elevated BP triggers abnormal failsafe."""
    is_crit, is_abnorm, reasons = evaluate_clinical_rules(
        heart_rate=76, systolic_bp=135, diastolic_bp=88, spo2=98.0, temperature=98.4
    )
    assert is_crit is False
    assert is_abnorm is True
    assert any("Blood Pressure elevated" in r for r in reasons)


def test_clinical_rule_normal():
    """Test that healthy vitals trigger no failsafe overrides."""
    is_crit, is_abnorm, reasons = evaluate_clinical_rules(
        heart_rate=72, systolic_bp=115, diastolic_bp=75, spo2=98.5, temperature=98.4
    )
    assert is_crit is False
    assert is_abnorm is False
    assert len(reasons) == 0


# ==========================================================
# 3. Clinical Remedies Generation Tests
# ==========================================================
def test_generate_remedies_critical():
    """Verify emergency dispatch and acute protocols are generated for Critical status."""
    vitals = {"heart_rate": 135, "systolic_bp": 185, "diastolic_bp": 115, "spo2": 88.0, "temperature": 103.5}
    remedies = generate_remedies_and_actions(vitals, "Critical")
    assert len(remedies) >= 2
    assert any("Emergency Dispatch" in r["title"] for r in remedies)
    assert any("Oxygen" in r["title"] for r in remedies)


def test_generate_remedies_normal():
    """Verify routine wellness guidance is provided for Normal status."""
    vitals = {"heart_rate": 72, "systolic_bp": 115, "diastolic_bp": 75, "spo2": 98.5, "temperature": 98.4}
    remedies = generate_remedies_and_actions(vitals, "Normal")
    assert any("Baseline Maintenance" in r["title"] for r in remedies)


# ==========================================================
# 4. Caretaker Alert Notification Tests
# ==========================================================
def test_send_caretaker_alert_dispatch():
    """Verify automated caretaker alert dispatches, generates message ID, and persists to log."""
    sample_vitals = {
        "heart_rate": 138,
        "systolic_bp": 190,
        "diastolic_bp": 120,
        "spo2": 88.0,
        "temperature": 102.5
    }
    res = send_caretaker_alert(
        patient_name="Unit Test Patient",
        vitals=sample_vitals,
        alert_level="Critical",
        recipient_email="caretaker_test@bytelife.ai",
        remedies=[{"title": "Test Action", "description": "Perform triage"}],
        override_reason="Unit test failsafe override"
    )
    assert res["success"] is True
    assert "message_id" in res
    assert res["alert_level"] == "Critical"
    assert res["recipient"] == "caretaker_test@bytelife.ai"

    # Check that audit log has the record
    history = get_alert_history()
    assert len(history) > 0
    assert history[0]["patient_name"] == "Unit Test Patient"


# ==========================================================
# 5. Career & Skill Intelligence Tests
# ==========================================================
def test_skill_extraction_from_resume():
    """Verify NLP skill extraction correctly recognizes technical keywords."""
    resume_text = "Proficient in Python, Pandas, NumPy, Power BI, DAX, Excel, and SQL for Healthcare Analytics."
    skills = extract_skills_from_text(resume_text)
    assert "python" in skills
    assert "pandas" in skills
    assert "power bi" in skills
    assert "microsoft excel" in skills
    assert "sql" in skills


def test_career_skill_gap_analysis():
    """Verify gap analysis produces valid match percentage and upskilling roadmap."""
    resume_text = "Experienced in Python, Pandas, NumPy, Power BI, and Microsoft Excel."
    result = analyze_career_skills(resume_text, target_role="Data Analyst")
    assert "target_evaluation" in result
    target = result["target_evaluation"]
    assert target["match_percentage"] > 20.0
    assert len(target["matched_skills"]) > 0
    assert len(result["upskilling_roadmap"]) > 0
    assert "readiness_summary" in result


# ==========================================================
# 6. Flask Endpoints Integration Tests
# ==========================================================
def test_flask_index_page(client):
    """Test dashboard index page returns 200 and loads HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Elderly &amp; Career Intelligence Hub" in response.data or b"Elderly & Career Intelligence Hub" in response.data


def test_flask_health_endpoint(client):
    """Test /health uptime endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_api_predict_health_normal(client):
    """Test /api/predict-health with normal physiological vitals."""
    payload = {
        "patient_name": "Test Senior",
        "heart_rate": 72,
        "systolic_bp": 115,
        "diastolic_bp": 75,
        "spo2": 98.5,
        "temperature": 98.4,
        "auto_alert": False
    }
    response = client.post("/api/predict-health", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["status_label"] == "Normal"
    assert data["status_code"] == 0
    assert data["rule_override"] is False


def test_api_predict_health_critical_with_alert(client):
    """Test /api/predict-health with critical vitals triggers automated caretaker alert."""
    payload = {
        "patient_name": "Critical Resident",
        "heart_rate": 135,
        "systolic_bp": 185,
        "diastolic_bp": 118,
        "spo2": 87.0,
        "temperature": 103.2,
        "recipient_email": "emergency_care@bytelife.ai",
        "auto_alert": True
    }
    response = client.post("/api/predict-health", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["status_label"] == "Critical"
    assert data["status_code"] == 2
    assert data["alert_info"] is not None
    assert data["alert_info"]["alert_level"] == "Critical"


def test_api_predict_health_input_validation(client):
    """Test input validation returns 400 for out-of-bounds or non-numeric metrics."""
    # Out of bounds heart rate
    bad_payload = {
        "heart_rate": 500,  # Impossible
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "spo2": 98,
        "temperature": 98.6
    }
    response = client.post("/api/predict-health", json=bad_payload)
    assert response.status_code == 400
    assert "bounds" in response.get_json()["error"]


def test_api_analyze_skills_endpoint(client):
    """Test /api/analyze-skills endpoint."""
    payload = {
        "resume_text": "Python, Power BI, SQL, Pandas, NumPy, Microsoft Excel",
        "target_role": "Data Analyst"
    }
    response = client.post("/api/analyze-skills", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["target_role"] == "Data Analyst"
    assert data["target_evaluation"]["match_percentage"] > 0
    assert len(data["target_evaluation"]["matched_skills"]) >= 4


def test_api_vitals_history_endpoint(client):
    """Test /api/vitals-history endpoint returns non-empty list."""
    response = client.get("/api/vitals-history")
    assert response.status_code == 200
    data = response.get_json()
    assert "history" in data
    assert data["count"] >= 1

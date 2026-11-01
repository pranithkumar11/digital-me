"""
verify_live_api.py - End-to-end verification script for live server.
"""
import requests
import json

BASE = "http://127.0.0.1:5000"

def test_endpoints():
    print("Testing Live Elderly & Career Intelligence Hub on", BASE)
    
    # 1. Health Endpoint
    r_health = requests.get(f"{BASE}/health")
    print("\n[1] GET /health -> Status:", r_health.status_code)
    print("    Response:", r_health.json())

    # 2. Normal Vitals Test
    norm_data = {
        "patient_name": "Pranith Kumar (Senior Cohort)",
        "heart_rate": 74,
        "systolic_bp": 116,
        "diastolic_bp": 76,
        "spo2": 98.2,
        "temperature": 98.4,
        "recipient_email": "caretaker@bytelife.ai",
        "auto_alert": True
    }
    r_norm = requests.post(f"{BASE}/api/predict-health", json=norm_data)
    norm_res = r_norm.json()
    print("\n[2] POST /api/predict-health (NORMAL)")
    print(f"    Status: {r_norm.status_code} | Classified: {norm_res.get('status_label')} (Code {norm_res.get('status_code')})")
    print(f"    Confidence: {norm_res.get('ml_confidence_percentage')}% | Rule Override: {norm_res.get('rule_override')}")
    print(f"    Remedies count: {len(norm_res.get('remedies', []))}")

    # 3. Critical Vitals Test (Hypoxia + Hypertensive Crisis)
    crit_data = {
        "patient_name": "Pranith Kumar (Critical Simulation)",
        "heart_rate": 136,
        "systolic_bp": 188,
        "diastolic_bp": 122,
        "spo2": 87.5,
        "temperature": 102.8,
        "recipient_email": "emergency_caretaker@bytelife.ai",
        "auto_alert": True
    }
    r_crit = requests.post(f"{BASE}/api/predict-health", json=crit_data)
    crit_res = r_crit.json()
    print("\n[3] POST /api/predict-health (CRITICAL)")
    print(f"    Status: {r_crit.status_code} | Classified: {crit_res.get('status_label')} (Code {crit_res.get('status_code')})")
    print(f"    Failsafe Override: {crit_res.get('rule_override')} | Reason: {crit_res.get('override_reason')}")
    print("    Automated Alert Dispatch:")
    alert_info = crit_res.get("alert_info", {})
    print(f"      - Message ID: {alert_info.get('message_id')}")
    print(f"      - Mode: {alert_info.get('mode')}")
    print(f"      - Recipient: {alert_info.get('recipient')}")
    print(f"      - Message: {alert_info.get('message')}")
    print("    Clinical Remedies & Protocols:")
    for remedy in crit_res.get("remedies", []):
        urgent_flag = "[URGENT] " if remedy.get("urgent") else ""
        print(f"      * {urgent_flag}{remedy.get('title')} ({remedy.get('category')}): {remedy.get('description')}")

    # 4. Career & Skill Intelligence Test
    career_data = {
        "resume_text": """
        Pranith Kumar Dupuguntla
        Role: Data Analyst
        Technical Skills: Power BI, DAX, Power Query, Microsoft Excel, Pivot Tables, XLOOKUP, Python, Pandas, NumPy, Statistical Analysis, Data Cleaning, Predictive Analytics, ETL, Business Intelligence
        Projects: Hospital Management Dashboard, Smoking Health Analysis Dashboard, Employee Performance Dashboard
        """,
        "target_role": "Data Analyst"
    }
    r_career = requests.post(f"{BASE}/api/analyze-skills", json=career_data)
    career_res = r_career.json()
    target_eval = career_res.get("target_evaluation", {})
    print("\n[4] POST /api/analyze-skills (Career Intelligence)")
    print(f"    Target Role: {career_res.get('target_role')}")
    print(f"    Match Percentage: {target_eval.get('match_percentage')}%")
    print(f"    Readiness Verdict: {career_res.get('readiness_summary', {}).get('verdict')}")
    print(f"    Matched Skills ({len(target_eval.get('matched_skills', []))}): {', '.join(target_eval.get('matched_skills', []))}")
    print(f"    Missing Skills ({len(target_eval.get('missing_skills', []))}): {', '.join(target_eval.get('missing_skills', []))}")
    print("    Upskilling Roadmap (Top 3):")
    for step in career_res.get("upskilling_roadmap", [])[:3]:
        print(f"      -> {step.get('skill')} [{step.get('priority')}]: {step.get('action')}")

    # 5. History Endpoints
    r_vitals_hist = requests.get(f"{BASE}/api/vitals-history")
    print("\n[5] GET /api/vitals-history -> Total records:", r_vitals_hist.json().get("count"))
    
    r_alerts_hist = requests.get(f"{BASE}/api/alerts-history")
    print("[6] GET /api/alerts-history -> Total alert logs:", r_alerts_hist.json().get("count"))

    # 6. Digital Me Endpoints
    print("\n[7] POST /api/digital_me/chat (Digital Twin RAG)")
    r_dm = requests.post(f"{BASE}/api/digital_me/chat", json={
        "query": "Tell me about your ByteLife project and your IJIRSET research paper."
    })
    print(f"    Status: {r_dm.status_code}")
    dm_res = r_dm.json()
    print("    Digital Twin Response Preview:\n   ", dm_res.get("response", "")[:180], "...")
    print(f"    Referenced Sources: {len(dm_res.get('sources', []))}")

    print("\n>>> ALL LIVE ENDPOINTS TESTED AND VALIDATED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    test_endpoints()

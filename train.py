"""
train.py - Health Vitals Classification Model Training Script
Part of the ByteLife Core Engine for Elderly & Career Intelligence Hub.
Trains and serializes a Machine Learning Classifier to predict patient status:
0: Normal, 1: Abnormal, 2: Critical.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "health_model.pkl")
METRICS_PATH = os.path.join(MODELS_DIR, "model_metrics.json")

def generate_synthetic_vitals_dataset(n_samples_per_class=1500, random_state=42):
    """
    Synthesize realistic physiological data across 3 classes:
    - Normal (0): Healthy stable vitals
    - Abnormal (1): Mild to moderate irregularities (elevated BP, mild fever, slight tachycardia/bradycardia)
    - Critical (2): Severe anomalies (hypoxemia, severe hypertensive crisis, extreme arrhythmia, hyperpyrexia)
    """
    np.random.seed(random_state)
    records = []

    # 1. Normal Samples (Label = 0)
    # Heart Rate: 60-95 bpm, Sys BP: 95-120 mmHg, Dia BP: 60-80 mmHg, SpO2: 95-99%, Temp: 97.2-98.8 F
    for _ in range(n_samples_per_class):
        hr = np.random.normal(74, 7)
        sys_bp = np.random.normal(112, 6)
        dia_bp = np.random.normal(72, 5)
        spo2 = np.random.uniform(95.0, 99.8)
        temp = np.random.normal(98.2, 0.4)
        
        # Clip to normal clinical boundaries
        hr = np.clip(hr, 60, 98)
        sys_bp = np.clip(sys_bp, 92, 122)
        dia_bp = np.clip(dia_bp, 60, 82)
        spo2 = np.clip(spo2, 95.0, 100.0)
        temp = np.clip(temp, 97.0, 98.9)
        records.append([hr, sys_bp, dia_bp, spo2, temp, 0])

    # 2. Abnormal Samples (Label = 1)
    # Subtypes: Prehypertension/Stage 1, low SpO2 (90-94%), low-grade fever, mild tachycardia/bradycardia
    for _ in range(n_samples_per_class):
        subtype = np.random.choice(["bp_abnormal", "spo2_abnormal", "temp_abnormal", "hr_abnormal"])
        # Defaults at baseline
        hr = np.random.uniform(62, 95)
        sys_bp = np.random.uniform(95, 120)
        dia_bp = np.random.uniform(65, 80)
        spo2 = np.random.uniform(95.0, 98.5)
        temp = np.random.uniform(97.5, 98.6)

        if subtype == "bp_abnormal":
            # Stage 1 hypertension or mild hypotension
            if np.random.rand() > 0.3:
                sys_bp = np.random.uniform(125, 145)
                dia_bp = np.random.uniform(82, 94)
            else:
                sys_bp = np.random.uniform(85, 92)
                dia_bp = np.random.uniform(55, 62)
        elif subtype == "spo2_abnormal":
            spo2 = np.random.uniform(90.0, 94.4)
        elif subtype == "temp_abnormal":
            # Low grade fever or mild hypothermia
            if np.random.rand() > 0.2:
                temp = np.random.uniform(99.2, 101.4)
            else:
                temp = np.random.uniform(95.5, 96.8)
        elif subtype == "hr_abnormal":
            if np.random.rand() > 0.5:
                hr = np.random.uniform(101, 118) # Mild tachycardia
            else:
                hr = np.random.uniform(50, 58)   # Mild bradycardia

        records.append([hr, sys_bp, dia_bp, spo2, temp, 1])

    # 3. Critical Samples (Label = 2)
    # Severe emergencies: Acute hypoxemia (<90%), Hypertensive emergency (>160 or >100), extreme HR, severe fever/hypothermia
    for _ in range(n_samples_per_class):
        emergency_type = np.random.choice(["hypoxia", "hypertensive_crisis", "shock_hypotension", "extreme_hr", "severe_fever"])
        hr = np.random.uniform(65, 95)
        sys_bp = np.random.uniform(100, 125)
        dia_bp = np.random.uniform(68, 82)
        spo2 = np.random.uniform(95.0, 98.5)
        temp = np.random.uniform(97.5, 98.6)

        if emergency_type == "hypoxia":
            spo2 = np.random.uniform(75.0, 89.4)
            hr = np.random.uniform(105, 140) # compensatory tachycardia
        elif emergency_type == "hypertensive_crisis":
            sys_bp = np.random.uniform(165, 215)
            dia_bp = np.random.uniform(105, 130)
        elif emergency_type == "shock_hypotension":
            sys_bp = np.random.uniform(65, 84)
            dia_bp = np.random.uniform(40, 54)
            hr = np.random.uniform(110, 150) # shock tachycardia
        elif emergency_type == "extreme_hr":
            if np.random.rand() > 0.5:
                hr = np.random.uniform(125, 175) # severe tachycardia / SVT
            else:
                hr = np.random.uniform(35, 48)   # severe bradycardia / AV block
        elif emergency_type == "severe_fever":
            temp = np.random.uniform(102.5, 105.5) # severe hyperpyrexia
            hr = np.random.uniform(105, 135)

        records.append([hr, sys_bp, dia_bp, spo2, temp, 2])

    columns = ["heart_rate", "systolic_bp", "diastolic_bp", "spo2", "temperature", "status"]
    df = pd.DataFrame(records, columns=columns)
    # Shuffle dataset
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return df

def train_health_model():
    """
    Trains a Random Forest classifier on synthetic vitals data and saves model artifacts.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    print(f"Generating synthetic vitals dataset...")
    df = generate_synthetic_vitals_dataset(n_samples_per_class=1500)
    
    feature_cols = ["heart_rate", "systolic_bp", "diastolic_bp", "spo2", "temperature"]
    X = df[feature_cols]
    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set size: {len(X_train)} | Test set size: {len(X_test)}")
    print("Training Random Forest Classifier...")

    model = RandomForestClassifier(
        n_estimators=120,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    # Predictions & Evaluation
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report_dict = classification_report(y_test, y_pred, target_names=["Normal", "Abnormal", "Critical"], output_dict=True)
    report_text = classification_report(y_test, y_pred, target_names=["Normal", "Abnormal", "Critical"])
    conf_mat = confusion_matrix(y_test, y_pred).tolist()

    print(f"Model Accuracy on Test Set: {acc * 100:.2f}%")
    print("\nClassification Report:\n", report_text)

    # Packaging model bundle
    bundle = {
        "model": model,
        "feature_names": feature_cols,
        "class_mapping": {0: "Normal", 1: "Abnormal", 2: "Critical"},
        "accuracy": float(acc),
        "metrics": report_dict,
        "trained_at": datetime.now().isoformat(),
        "model_type": "RandomForestClassifier",
        "version": "1.0.0"
    }

    joblib.dump(bundle, MODEL_PATH)
    print(f"Model saved successfully to: {MODEL_PATH}")

    # Save metrics JSON for quick inspection
    metrics_summary = {
        "accuracy": acc,
        "report": report_dict,
        "confusion_matrix": conf_mat,
        "trained_at": bundle["trained_at"],
        "dataset_shape": df.shape
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_summary, f, indent=2)
    print(f"Metrics saved to: {METRICS_PATH}")

    return bundle

if __name__ == "__main__":
    train_health_model()

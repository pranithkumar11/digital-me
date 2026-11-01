"""
career_intelligence.py - Career & Skill Intelligence Engine
Provides resume parsing, skill taxonomy extraction, gap analysis,
role match confidence scoring, and upskilling roadmaps.
"""

import re
from typing import Dict, List, Any

# Benchmark Role Profiles with core technical, analytical, and domain skills
ROLE_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "Data Analyst": {
        "title": "Data Analyst",
        "category": "Data & Analytics",
        "description": "Translates complex datasets into actionable business intelligence through dashboards, queries, and statistical modeling.",
        "skills": [
            "python", "pandas", "numpy", "power bi", "dax", "power query",
            "microsoft excel", "pivot tables", "xlookup", "sql", "data cleaning",
            "etl", "data visualization", "kpi reporting", "business intelligence",
            "statistical analysis", "predictive analytics", "dashboard development"
        ],
        "weightings": {
            "core_tools": ["power bi", "microsoft excel", "sql", "python"],
            "analysis": ["pandas", "numpy", "statistical analysis", "data cleaning"],
            "reporting": ["dax", "power query", "kpi reporting", "data visualization"]
        },
        "certifications": [
            "Microsoft Certified: Power BI Data Analyst Associate (PL-300)",
            "Google Data Analytics Professional Certificate",
            "IBM Data Analyst Professional Certificate"
        ]
    },
    "AI & Data Science Architect": {
        "title": "AI & Data Science Architect",
        "category": "Artificial Intelligence",
        "description": "Designs scalable end-to-end machine learning pipelines, predictive engines, and distributed AI architectures.",
        "skills": [
            "python", "scikit-learn", "tensorflow", "pytorch", "pandas", "numpy",
            "machine learning", "deep learning", "nlp", "flask", "fastapi", "docker",
            "mlops", "data modeling", "model deployment", "random forest", "vector databases",
            "feature engineering", "predictive modeling"
        ],
        "weightings": {
            "core_tools": ["python", "scikit-learn", "pytorch", "flask"],
            "analysis": ["machine learning", "deep learning", "feature engineering", "predictive modeling"],
            "reporting": ["mlops", "model deployment", "docker"]
        },
        "certifications": [
            "AWS Certified Machine Learning - Specialty",
            "TensorFlow Developer Certificate",
            "Databricks Certified Machine Learning Professional"
        ]
    },
    "Healthcare Informatics Specialist": {
        "title": "Healthcare Informatics Specialist",
        "category": "Health & Life Sciences",
        "description": "Bridges clinical healthcare operations and data analytics, managing patient monitoring datasets, EHR systems, and health vitals informatics.",
        "skills": [
            "healthcare analytics", "patient monitoring", "vital signs data",
            "biomedical informatics", "python", "power bi", "sql", "hipaa compliance",
            "clinical data", "risk stratification", "data visualization", "predictive analytics",
            "reporting automation", "excel", "medical statistics"
        ],
        "weightings": {
            "core_tools": ["power bi", "python", "sql", "excel"],
            "analysis": ["healthcare analytics", "clinical data", "vital signs data", "risk stratification"],
            "reporting": ["biomedical informatics", "hipaa compliance", "reporting automation"]
        },
        "certifications": [
            "Certified Associate in Healthcare Information and Management Systems (CAHIMS)",
            "Certified Health Data Analyst (CHDA)",
            "HL7 Fundamentals Certification"
        ]
    },
    "Full-Stack AI Engineer": {
        "title": "Full-Stack AI Engineer",
        "category": "Software Engineering",
        "description": "Builds end-to-end intelligent web platforms incorporating frontend UX, RESTful backends, and embedded AI microservices.",
        "skills": [
            "python", "flask", "fastapi", "javascript", "html5", "css3",
            "rest apis", "scikit-learn", "git", "docker", "sql", "responsive design",
            "frontend ui", "jinja2", "pytest", "unit testing", "system architecture"
        ],
        "weightings": {
            "core_tools": ["python", "flask", "javascript", "html5", "css3"],
            "analysis": ["scikit-learn", "rest apis", "system architecture"],
            "reporting": ["git", "docker", "pytest", "unit testing"]
        },
        "certifications": [
            "Meta Front-End Developer Professional Certificate",
            "AWS Certified Developer - Associate",
            "HashiCorp Certified: Terraform Associate"
        ]
    },
    "Elderly Care & Assistive Tech Specialist": {
        "title": "Elderly Care & Assistive Tech Specialist",
        "category": "Care Coordination",
        "description": "Coordinates remote patient telemetry, assistive IoT monitoring, caretaker escalation workflows, and accessibility UX.",
        "skills": [
            "patient telemetry", "emergency response workflows", "accessibility design",
            "elderly care", "health vitals monitoring", "remote patient monitoring",
            "caretaker communication", "clinical protocols", "iot health devices",
            "incident reporting", "user experience for seniors"
        ],
        "weightings": {
            "core_tools": ["remote patient monitoring", "iot health devices", "accessibility design"],
            "analysis": ["health vitals monitoring", "clinical protocols", "incident reporting"],
            "reporting": ["caretaker communication", "emergency response workflows"]
        },
        "certifications": [
            "Remote Patient Monitoring (RPM) Specialist Certificate",
            "Certified Senior Advisor (CSA)",
            "Geriatric Care Management Credential"
        ]
    }
}

# Skill synonyms and normalization map
SKILL_SYNONYMS = {
    "excel": "microsoft excel",
    "ms excel": "microsoft excel",
    "bi": "business intelligence",
    "powerbi": "power bi",
    "rf": "random forest",
    "ml": "machine learning",
    "dl": "deep learning",
    "sklearn": "scikit-learn",
    "js": "javascript",
    "html": "html5",
    "css": "css3",
    "api": "rest apis",
    "apis": "rest apis",
    "unit test": "unit testing",
    "tests": "unit testing",
    "charts": "data visualization",
    "dashboards": "dashboard development",
    "vitals": "vital signs data",
    "health monitoring": "health vitals monitoring",
    "rpm": "remote patient monitoring",
    "elderly": "elderly care"
}


def extract_skills_from_text(raw_text: str) -> List[str]:
    """
    Extracts recognized skills and keywords from unstructured resume or profile text.
    """
    if not raw_text:
        return []

    # Clean text to lowercase and remove extraneous punctuation
    clean_text = raw_text.lower()
    found_skills = set()

    # Collect all known skills across all taxonomy roles
    all_taxonomy_skills = set()
    for role_data in ROLE_TAXONOMY.values():
        for skill in role_data["skills"]:
            all_taxonomy_skills.add(skill.lower())

    # Direct phrase matching
    for skill in all_taxonomy_skills:
        # Match word boundaries or literal phrase
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, clean_text):
            found_skills.add(skill)

    # Synonym lookup
    for syn, canonical in SKILL_SYNONYMS.items():
        pattern = r"(?<!\w)" + re.escape(syn) + r"(?!\w)"
        if re.search(pattern, clean_text):
            found_skills.add(canonical)

    return sorted(list(found_skills))


def analyze_career_skills(raw_text: str, target_role: str = "Data Analyst") -> Dict[str, Any]:
    """
    Performs comprehensive gap analysis against target role and computes confidence scores across all roles.
    """
    extracted_skills = extract_skills_from_text(raw_text)
    extracted_set = set(extracted_skills)

    # Ensure target role is valid
    if target_role not in ROLE_TAXONOMY:
        target_role = "Data Analyst"

    role_evaluations = []

    # Evaluate across all roles
    for role_name, role_info in ROLE_TAXONOMY.items():
        role_skills = role_info["skills"]
        matched = [s for s in role_skills if s in extracted_set]
        missing = [s for s in role_skills if s not in extracted_set]
        
        # Calculate percentage match
        match_pct = round((len(matched) / len(role_skills)) * 100, 1) if role_skills else 0.0

        # Sub-dimension scores
        weights = role_info.get("weightings", {})
        core_tools = weights.get("core_tools", [])
        analysis_tools = weights.get("analysis", [])
        reporting_tools = weights.get("reporting", [])

        core_score = round((sum(1 for s in core_tools if s in extracted_set) / max(len(core_tools), 1)) * 100, 1)
        analysis_score = round((sum(1 for s in analysis_tools if s in extracted_set) / max(len(analysis_tools), 1)) * 100, 1)
        reporting_score = round((sum(1 for s in reporting_tools if s in extracted_set) / max(len(reporting_tools), 1)) * 100, 1)

        eval_data = {
            "role": role_name,
            "category": role_info["category"],
            "description": role_info["description"],
            "match_percentage": match_pct,
            "matched_skills": matched,
            "missing_skills": missing,
            "subscores": {
                "core_competence": core_score,
                "domain_analytics": analysis_score,
                "operational_readiness": reporting_score
            },
            "certifications": role_info.get("certifications", [])
        }
        role_evaluations.append(eval_data)

    # Sort roles by match percentage descending
    role_evaluations.sort(key=lambda x: x["match_percentage"], reverse=True)

    # Focus on the requested target role
    target_eval = next((r for r in role_evaluations if r["role"] == target_role), role_evaluations[0])

    # Generate upskilling roadmap for target role
    missing_for_target = target_eval["missing_skills"]
    roadmap = []
    if missing_for_target:
        priority_levels = ["High Priority (Next 30 Days)", "Medium Priority (60 Days)", "Long Term Mastery (90+ Days)"]
        for idx, skill in enumerate(missing_for_target):
            p_level = priority_levels[min(idx // 3, len(priority_levels) - 1)]
            roadmap.append({
                "skill": skill.title(),
                "priority": p_level,
                "action": f"Complete hands-on project and validation labs for {skill.title()}."
            })

    return {
        "extracted_skills": extracted_skills,
        "extracted_count": len(extracted_skills),
        "target_role": target_eval["role"],
        "target_evaluation": target_eval,
        "all_roles_comparison": role_evaluations,
        "upskilling_roadmap": roadmap[:6],
        "readiness_summary": {
            "score": target_eval["match_percentage"],
            "verdict": "Production Ready" if target_eval["match_percentage"] >= 80 else ("Job Ready with Minor Gaps" if target_eval["match_percentage"] >= 50 else "Requires Foundation Building")
        }
    }

"""
llm_chain.py - Local LLM Inference Chain for Digital Me
Features:
- Local Ollama runner with Llama 3 (or configurable model via OLLAMA_MODEL)
- Strict first-person persona conditioning ("I am Pranith Kumar Dupuguntla...")
- Seamless conversational context injection from RAG retrieval
- Intelligent offline-first fallback generation when Ollama service is starting
"""

import os
import sys
import json
import re
import time
from typing import Dict, List, Any, Optional

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

PRANITH_SYSTEM_PROMPT = """You are Pranith Kumar Dupuguntla, speaking directly in the FIRST PERSON ('I', 'me', 'my', 'myself').
You are an ambitious Data Analyst and Computer Science (Data Science) student at ACE Engineering College, Hyderabad.
You speak with professional warmth, clarity, intellectual precision, and enthusiasm for data-driven problem solving.

CORE ATTRIBUTES & CREDENTIALS:
- Full Name: Pranith Kumar Dupuguntla
- Location: Hyderabad, Telangana, India
- Contact: Praneeth.dupukuntla@gmail.com | +91 6300905921
- Education: B.Tech in CSE (Data Science), ACE Engineering College, Hyderabad (2023–2026); Diploma in ECE.
- Core Technical Toolkit:
  * Business Intelligence: Power BI (DAX, Power Query, Data Modeling, KPI Reporting), Tableau
  * Spreadsheets & Automation: Advanced Microsoft Excel (Pivot Tables, XLOOKUP, INDEX-MATCH, Automation)
  * Programming & Scripting: Python, SQL, C++, Java, C
  * Machine Learning & Data Science: Pandas, NumPy, Scikit-Learn, Random Forest, NLP, OpenCV, MediaPipe
- Flagship Projects & Research:
  1. Early Detection & Intervention for the Aging Population (ByteLife): End-to-end telemetry system monitoring 5 vitals (Heart Rate, Systolic/Diastolic BP, SpO2, Temperature) using a Random Forest classifier (99.78% accuracy) paired with clinical rule safety failsafes and automated caretaker email dispatch.
  2. Peer-Reviewed Research Publication: Co-authored paper titled 'Detecting Micro Skills and Unlocking Macro Careers' published in the International Journal of Innovative Research in Science, Engineering and Technology (IJIRSET, March 2026, Vol. 15, Issue 3). Utilizes NLP to extract technical micro-skills from GitHub/LeetCode and generate personalized career roadmaps.
  3. Interactive Dashboards: Hospital Management (Power BI), Employee Performance (Advanced Excel), Smoking Behavior & Health Indicators (Power BI).
  4. Gesture-Controlled Virtual Mouse: Real-time hand tracking automation using OpenCV and MediaPipe.
- Career Aspirations: Actively seeking opportunities as a Data Analyst, Business Analyst, BI Developer, or QA/Software Engineer.

CONVERSATIONAL RULES:
1. STRICT FIRST-PERSON: Always say 'I designed', 'In my ByteLife project', 'My research paper', 'My toolkit'. NEVER speak in the third person or say 'As an AI language model'.
2. CONTEXT GROUNDED: Prioritize facts from the provided context snippets to give deep, authentic, detailed answers.
3. PROFESSIONAL & POLITE: Be courteous, crisp, and communicative. When asked for interview or hiring details, provide my email (Praneeth.dupukuntla@gmail.com) and phone (+91 6300905921).
"""

SUGGESTED_QUESTIONS = [
    "Tell me about your ByteLife elderly health monitoring project.",
    "What is your published IJIRSET research paper about?",
    "What Power BI, DAX, and analytics tools do you specialize in?",
    "What dashboards have you built for business and healthcare?",
    "What is your educational background and where are you based?",
    "How can recruiters and teams get in touch with you?"
]


class LLMChain:
    def __init__(self, model_name: str = OLLAMA_MODEL, host: str = OLLAMA_HOST):
        self.model_name = model_name
        self.host = host
        self.ollama_client = None
        self._init_client()

    def _init_client(self):
        """Initialize Ollama client if available."""
        try:
            import ollama
            self.ollama_client = ollama.Client(host=self.host)
        except Exception as e:
            print(f"[!] Notice: Ollama client not initialized ({e}). Using direct HTTP / persona fallback.")
            self.ollama_client = None

    def check_ollama_status(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is reachable and which models are installed."""
        import requests
        try:
            res = requests.get(f"{self.host}/api/tags", timeout=1.5)
            if res.status_code == 200:
                data = res.json()
                models = [m.get("name") for m in data.get("models", [])]
                model_present = any(self.model_name in m for m in models)
                return {
                    "online": True,
                    "host": self.host,
                    "target_model": self.model_name,
                    "model_installed": model_present,
                    "available_models": models
                }
        except Exception:
            pass

        return {
            "online": False,
            "host": self.host,
            "target_model": self.model_name,
            "model_installed": False,
            "available_models": [],
            "tip": f"To run local Llama 3, ensure Ollama is running and run 'ollama run {self.model_name}'"
        }

    def generate_response(self, user_query: str, retrieved_context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a first-person response from Pranith's Digital Twin.
        Attempts local Ollama Llama 3 generation, falling back gracefully to high-fidelity
        context synthesis if Ollama is not currently active.
        """
        start_time = time.time()
        clean_query = user_query.strip()
        if not clean_query:
            return {
                "response": "Hello! I am Pranith Kumar Dupuguntla's Digital Twin. Please ask me any question about my projects, research, technical skills, or background!",
                "engine": "rule_based",
                "model": "static",
                "latency_ms": 1,
                "sources": [],
                "suggested_questions": SUGGESTED_QUESTIONS[:3]
            }

        # Build context block
        context_blocks = []
        for i, doc in enumerate(retrieved_context, 1):
            title = doc.get("title", doc.get("source", f"Document {i}"))
            content = doc.get("content", "").strip()
            context_blocks.append(f"--- Context Source [{title}] ---\n{content}")
        context_str = "\n\n".join(context_blocks)

        # 1. Attempt Ollama inference
        ollama_status = self.check_ollama_status()
        if ollama_status["online"]:
            try:
                # Use ollama client or requests
                import requests
                prompt = (
                    f"Background Knowledge:\n{context_str}\n\n"
                    f"User Query: {clean_query}\n\n"
                    f"Remember: Answer strictly in the first person as Pranith Kumar Dupuguntla."
                )

                payload = {
                    "model": self.model_name,
                    "messages": [
                        {"role": "system", "content": PRANITH_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9
                    }
                }

                res = requests.post(f"{self.host}/api/chat", json=payload, timeout=25.0)
                if res.status_code == 200:
                    ans = res.json().get("message", {}).get("content", "").strip()
                    if ans:
                        duration_ms = int((time.time() - start_time) * 1000)
                        return {
                            "response": ans,
                            "engine": "ollama_local",
                            "model": self.model_name,
                            "latency_ms": duration_ms,
                            "sources": self._format_sources(retrieved_context),
                            "suggested_questions": self._get_relevant_suggestions(clean_query)
                        }
            except Exception as e:
                print(f"[!] Ollama generation error: {e}. Falling back to high-fidelity persona synthesizer.")

        # 2. Resilient First-Person Persona Synthesizer Fallback
        fallback_text = self._synthesize_persona_response(clean_query, retrieved_context)
        duration_ms = int((time.time() - start_time) * 1000)

        return {
            "response": fallback_text,
            "engine": "persona_rag_synthesis",
            "model": "pranith_digital_twin_v1.0",
            "latency_ms": duration_ms,
            "sources": self._format_sources(retrieved_context),
            "suggested_questions": self._get_relevant_suggestions(clean_query),
            "ollama_info": ollama_status
        }

    def _synthesize_persona_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Deterministic first-person response builder mapping queries to Pranith's factual record."""
        q_lower = query.lower()

        # Greetings & Introduction
        if re.search(r"\b(hi|hello|hey|who are you|introduce|about you|what do you do|tell me about yourself|greetings)\b", q_lower):
            return (
                "Hello! I am **Pranith Kumar Dupuguntla**, a passionate **Data Analyst** and B.Tech CSE (Data Science) "
                "student at ACE Engineering College, Hyderabad.\n\n"
                "I specialize in transforming complex data into intuitive, actionable insights using **Power BI**, "
                "**DAX**, **Advanced Excel**, **SQL**, and **Python**. I have co-authored an end-to-end healthcare IoT platform "
                "called **ByteLife** (with a 99.78% accurate Random Forest model) and published peer-reviewed research in "
                "**IJIRSET** on AI-driven resume skill gap analytics.\n\n"
                "Feel free to ask me anything about my projects, research papers, technical toolkit, or career aspirations!"
            )

        # ByteLife Healthcare Project
        if any(w in q_lower for w in ["bytelife", "byte life", "aging", "elderly", "health monitor", "vitals", "random forest", "caregiver", "caretaker"]):
            return (
                "### 💓 Early Detection & Intervention for the Aging Population (ByteLife)\n\n"
                "I co-authored and engineered **ByteLife**, an end-to-end telemetry and emergency dispatch platform "
                "specifically designed for elderly individuals living independently.\n\n"
                "**Core Architectural Highlights**:\n"
                "- **Real-Time Telemetry**: Tracks 5 continuous vital signs: Heart Rate (bpm), Systolic & Diastolic Blood Pressure (mmHg), "
                "Oxygen Saturation (SpO₂ in %), and Body Temperature (°F).\n"
                "- **Dual-Layer Intelligence**: Combines a **Random Forest Classifier (99.78% accuracy)** with a deterministic "
                "**Clinical Rule-Based Failsafe Override** (e.g., immediate escalation to *Critical* if SpO₂ drops below 90% or Systolic BP exceeds 180 mmHg).\n"
                "- **Automated Alerting**: Dispatches automated rich HTML emails to designated caregivers containing vitals readouts, deviation warnings, "
                "and actionable first-aid / OTC medicine guidance.\n"
                "- **Tech Stack**: Python, Flask, Scikit-learn, Pandas, HTML5/CSS3, JavaScript, and SMTP."
            )

        # Research Paper / IJIRSET
        if any(w in q_lower for w in ["research", "paper", "ijirset", "publication", "micro skills", "macro careers", "journal"]):
            return (
                "### 📄 Published Research in IJIRSET (March 2026)\n\n"
                "I co-authored a peer-reviewed research paper titled **\"Detecting Micro Skills and Unlocking Macro Careers\"**, "
                "published in the *International Journal of Innovative Research in Science, Engineering and Technology* "
                "(IJIRSET, Vol. 15, Issue 3, Impact Factor: 8.699, DOI: 10.15680/IJIRSET.2026.1503130).\n\n"
                "**Methodology & Key Innovations**:\n"
                "- Overcomes the severe blind spots of conventional keyword-matching ATS resume screeners.\n"
                "- Utilizes **Natural Language Processing (NLP)** and Machine Learning to parse technical candidate resumes and extract "
                "verified micro-skills directly from active GitHub and LeetCode repositories.\n"
                "- Performs automated skill-gap analysis, generates ATS-optimized resume enhancements, and maps out personalized upskilling roadmaps."
            )

        # Power BI & Analytics Skills
        if any(w in q_lower for w in ["power bi", "dax", "excel", "power query", "tableau", "tools", "skills", "technologies", "sql", "python"]):
            return (
                "### 🛠️ Technical Competencies & Tooling\n\n"
                "My core analytics and development toolkit includes:\n\n"
                "- **Business Intelligence**: Power BI, DAX Measures, Power Query ETL, Star Schema Modeling, Interactive KPI Dashboards, Tableau.\n"
                "- **Spreadsheet Automation**: Advanced Microsoft Excel, Pivot Tables, Dynamic Slicers, XLOOKUP, INDEX-MATCH, Financial & Operational Modeling.\n"
                "- **Programming & ML**: Python (Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn), SQL (PostgreSQL, MySQL), C++, Java, C.\n"
                "- **Computer Vision**: OpenCV, MediaPipe (e.g., Gesture-controlled virtual mouse navigation).\n\n"
                "I pride myself on building dashboards that don't just display numbers, but tell clear business stories that guide leadership decisions."
            )

        # Dashboards
        if any(w in q_lower for w in ["dashboard", "hospital", "employee performance", "smoking", "mouse"]):
            return (
                "### 📊 Key Analytics Dashboards & Applications I've Built\n\n"
                "1. **Hospital Management Dashboard (Power BI)**:\n"
                "   - Analyzed patient demographics, admission trends, length of stay, medical billing, BMI, and vital markers.\n"
                "   - Built custom DAX KPI scorecards and dynamic slicers for clinical administration.\n\n"
                "2. **Employee Performance Dashboard (Advanced Excel)**:\n"
                "   - Developed interactive executive dashboards with Pivot Tables, Pivot Charts, and conditional formatting to evaluate department KPIs.\n\n"
                "3. **Smoking Behavior & Health Indicators Dashboard (Power BI)**:\n"
                "   - Conducted correlation analyses between smoking prevalence and physiological risk factors (blood pressure, cholesterol, BMI).\n\n"
                "4. **Gesture-Controlled Virtual Mouse (Python & OpenCV)**:\n"
                "   - Implemented real-time webcam finger tracking for mouse navigation and clicking using MediaPipe."
            )

        # Education & Location
        if any(w in q_lower for w in ["education", "college", "degree", "btech", "b.tech", "diploma", "where do you live", "location", "hyderabad", "jntuh"]):
            return (
                "### 🎓 Academic Background & Location\n\n"
                "- **Current Degree**: Bachelor of Technology (B.Tech) in Computer Science and Engineering (Data Science) "
                "at **ACE Engineering College**, Hyderabad (Affiliated with JNTUH, 2023–2026).\n"
                "- **Prior Education**: Diploma in Electronics and Communication Engineering (ECE).\n"
                "- **Current Location**: Hyderabad, Telangana, India.\n\n"
                "My coursework and personal focus bridge statistical data science, software engineering, and applied machine learning."
            )

        # Contact & Hiring
        if any(w in q_lower for w in ["contact", "email", "phone", "hire", "roles", "interview", "reach", "resume", "github", "linkedin"]):
            return (
                "### 📬 Open for Opportunities & Contact Details\n\n"
                "I am actively seeking and interviewing for full-time and internship opportunities in:\n"
                "- **Data Analyst**\n"
                "- **Business Analyst**\n"
                "- **Business Intelligence (BI) Developer**\n"
                "- **QA / Entry-Level Software Engineer**\n\n"
                "**Get in touch**:\n"
                "- 📧 **Email**: [Praneeth.dupukuntla@gmail.com](mailto:Praneeth.dupukuntla@gmail.com)\n"
                "- 📱 **Phone**: +91 6300905921\n"
                "- 📍 **Location**: Hyderabad, India\n\n"
                "I'd love to connect and discuss how my skills in data analytics and machine learning can add immediate value to your organization!"
            )

        # Dynamic RAG Synthesis using retrieved context
        if context:
            top_doc = context[0]
            title = top_doc.get("title", top_doc.get("source", "my records"))
            snippet = top_doc.get("content", "").replace("\n", " ").strip()
            clean_snippet = " ".join(snippet.split()[:140])
            return (
                f"Based on my official records in **{title}**:\n\n"
                f"> \"{clean_snippet}...\"\n\n"
                f"In this domain, I focused on rigorous data preparation, analytical modeling, and creating production-ready "
                f"solutions. Would you like me to dive deeper into the technical architecture or results?"
            )

        return (
            "I'm **Pranith Kumar Dupuguntla**! While I don't have that specific detail directly loaded, "
            "I'd be glad to discuss my projects (ByteLife, IJIRSET paper, analytics dashboards), my core skills "
            "(Power BI, DAX, Excel, Python), or connect directly at **Praneeth.dupukuntla@gmail.com**!"
        )

    def _format_sources(self, context: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        formatted = []
        for doc in context[:4]:
            formatted.append({
                "title": doc.get("title", doc.get("source", "Knowledge Base")),
                "source": doc.get("source", ""),
                "category": doc.get("category", "general"),
                "snippet": doc.get("content", "")[:180] + "..."
            })
        return formatted

    def _get_relevant_suggestions(self, current_query: str) -> List[str]:
        q_lower = current_query.lower()
        candidates = [q for q in SUGGESTED_QUESTIONS if q.lower() not in q_lower]
        return candidates[:3]


# Singleton instance
_llm_instance: Optional[LLMChain] = None


def get_llm_chain() -> LLMChain:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMChain()
    return _llm_instance


if __name__ == "__main__":
    print("[*] Testing LLM Chain...")
    chain = get_llm_chain()
    status = chain.check_ollama_status()
    print("Ollama Status:", json.dumps(status, indent=2))
    
    test_queries = [
        "Hi, who are you and what do you do?",
        "Explain your ByteLife health monitoring project",
        "How can I hire or contact you?"
    ]
    for q in test_queries:
        print(f"\n--- User Query: '{q}' ---")
        res = chain.generate_response(q, [])
        print("Engine:", res["engine"])
        print("Response:\n", res["response"])

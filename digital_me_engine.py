"""
digital_me_engine.py - Core Engine for Pranith Kumar Dupuguntla's Digital Twin
Provides semantic RAG retrieval, persona-conditioned response generation,
and smart first-person synthesis with multi-model LLM support.
"""

import os
import sys
import re
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_digital_me")
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
CURRENT_PROFILE_PATH = os.path.join(DATA_DIR, "current_profile.json")

os.makedirs(PROFILES_DIR, exist_ok=True)

def get_current_profile() -> Dict[str, Any]:
    """Retrieve the currently active person profile."""
    if os.path.exists(CURRENT_PROFILE_PATH):
        try:
            with open(CURRENT_PROFILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading current profile: {e}")

    # Default fallback profile
    return {
        "id": "pranith_kumar",
        "name": "Pranith Kumar Dupuguntla",
        "role": "Data Analyst",
        "specialization": "CSE (Data Science)",
        "location": "Hyderabad, India",
        "email": "Praneeth.dupukuntla@gmail.com",
        "phone": "+91 6300905921",
        "education": "Bachelor of Technology (B.Tech) in CSE (Data Science), ACE Engineering College, Hyderabad (Affiliated with JNTUH, 2023–2026)",
        "bio": "Passionate Data Analyst skilled in Power BI, Advanced Excel, Python, and SQL. Experienced in predictive analytics, star-schema data modeling, interactive KPI dashboards, real-time healthcare telemetry, and published research in NLP-driven skill analytics.",
        "skills": ["Power BI", "DAX", "Power Query", "Microsoft Excel", "Python", "SQL", "Tableau", "Pandas", "Scikit-Learn"],
        "projects": [
            {
                "title": "Early Detection & Intervention for Aging Population (ByteLife)",
                "category": "Healthcare Telemetry & AI",
                "description": "Real-time vitals monitoring with Random Forest classifier (99.78% acc) and automated caretaker alerts.",
                "tech": ["Python", "Flask", "Scikit-Learn", "SMTP"]
            },
            {
                "title": "Detecting Micro Skills & Unlocking Macro Careers",
                "category": "Published Research Paper (IJIRSET)",
                "description": "Published paper in IJIRSET on AI resume parsing, LeetCode/GitHub micro-skill extraction, and skill gap analytics.",
                "tech": ["NLP", "Machine Learning", "Python"]
            }
        ],
        "target_roles": ["Data Analyst", "Business Analyst", "BI Developer", "Quality Assurance", "Software Engineer"]
    }

def list_all_profiles() -> List[Dict[str, Any]]:
    """List summary of all saved person profiles."""
    profiles = []
    if os.path.exists(PROFILES_DIR):
        for f in os.listdir(PROFILES_DIR):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(PROFILES_DIR, f), "r", encoding="utf-8") as fp:
                        pdata = json.load(fp)
                        profiles.append({
                            "id": pdata.get("id", f.replace(".json", "")),
                            "name": pdata.get("name", "Unknown"),
                            "role": pdata.get("role", "Professional"),
                            "location": pdata.get("location", ""),
                            "skills_count": len(pdata.get("skills", [])),
                            "projects_count": len(pdata.get("projects", []))
                        })
                except Exception:
                    pass
    return profiles

def save_person_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Save or update a person profile and sync current active profile."""
    name = profile_data.get("name", "Unnamed Profile").strip()
    profile_id = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_") or "custom_profile"
    profile_data["id"] = profile_id

    # Ensure arrays
    if isinstance(profile_data.get("skills"), str):
        profile_data["skills"] = [s.strip() for s in profile_data["skills"].split(",") if s.strip()]
    if isinstance(profile_data.get("target_roles"), str):
        profile_data["target_roles"] = [r.strip() for r in profile_data["target_roles"].split(",") if r.strip()]

    # Save to profiles/
    file_path = os.path.join(PROFILES_DIR, f"{profile_id}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    # Set as current
    with open(CURRENT_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    # Sync a profile summary into knowledge base
    kb_profile_path = os.path.join(KB_DIR, f"profile_{profile_id}.txt")
    with open(kb_profile_path, "w", encoding="utf-8") as f:
        f.write(f"# Person Profile: {name}\n")
        f.write(f"Role: {profile_data.get('role')}\n")
        f.write(f"Location: {profile_data.get('location')}\n")
        f.write(f"Email: {profile_data.get('email')} | Phone: {profile_data.get('phone')}\n")
        f.write(f"Education: {profile_data.get('education')}\n")
        f.write(f"Bio: {profile_data.get('bio')}\n")
        f.write(f"Skills: {', '.join(profile_data.get('skills', []))}\n\n")
        f.write("Projects:\n")
        for p in profile_data.get("projects", []):
            if isinstance(p, dict):
                f.write(f"- {p.get('title')}: {p.get('description')} (Tech: {', '.join(p.get('tech', []))})\n")
            elif isinstance(p, str):
                f.write(f"- {p}\n")
        if profile_data.get("custom_qa"):
            f.write(f"\nPersonal Q&A:\n{profile_data.get('custom_qa')}\n")

    return profile_data

_VECTORSTORE = None
_EMBEDDINGS = None

def get_embeddings():
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        from langchain_community.embeddings import FastEmbedEmbeddings
        _EMBEDDINGS = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return _EMBEDDINGS

def get_vectorstore():
    global _VECTORSTORE
    if _VECTORSTORE is None:
        from langchain_chroma import Chroma
        if os.path.exists(PERSIST_DIR):
            _VECTORSTORE = Chroma(
                persist_directory=PERSIST_DIR,
                embedding_function=get_embeddings()
            )
        else:
            # Fallback to building index if not yet present
            from build_digital_me_index import build_index
            _VECTORSTORE = build_index()
    return _VECTORSTORE

def search_knowledge_base(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve top-k relevant knowledge chunks."""
    try:
        vs = get_vectorstore()
        docs = vs.similarity_search(query, k=k)
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "Knowledge Base"),
                "title": doc.metadata.get("title", doc.metadata.get("source", "Document")),
                "category": doc.metadata.get("category", "general"),
                "chunk_id": doc.metadata.get("chunk_id", "")
            })
        return results
    except Exception as e:
        print(f"[!] Vector retrieval error: {e}. Falling back to file scan.")
        return fallback_file_search(query, k=k)

def fallback_file_search(query: str, k: int = 3) -> List[Dict[str, Any]]:
    """Keyword search fallback if Chroma vectorstore is unavailable."""
    results = []
    tokens = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 3]
    if not os.path.exists(KB_DIR):
        return results

    for fname in os.listdir(KB_DIR):
        if not fname.endswith(".txt"):
            continue
        fpath = os.path.join(KB_DIR, fname)
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        score = sum(content.lower().count(token) for token in tokens)
        if score > 0:
            # Extract most relevant snippet
            pos = 0
            for token in tokens:
                p = content.lower().find(token)
                if p != -1:
                    pos = max(0, p - 100)
                    break
            snippet = content[pos:pos+450].replace("\n", " ").strip()
            results.append({
                "content": snippet,
                "source": fname,
                "title": fname.replace(".txt", "").replace("_", " ").title(),
                "category": "keyword_match",
                "score": score
            })

    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return results[:k]

SYSTEM_PERSONA_PROMPT = """You are the official Digital Twin of Pranith Kumar Dupuguntla.
You speak in the FIRST PERSON ('I', 'me', 'my').
Key Persona Attributes:
- Role: Data Analyst and B.Tech CSE (Data Science) Student at ACE Engineering College, Hyderabad.
- Expertise: Power BI (DAX, Power Query, Modeling), Python (Pandas, NumPy, Scikit-Learn), SQL, Tableau, Advanced Excel.
- Projects:
  1. ByteLife Core: Senior real-time health monitoring with Random Forest (99.78% accuracy), rule-based clinical safety overrides, and automated caretaker email dispatch.
  2. Published Research: Co-authored in IJIRSET (March 2026) titled 'Detecting Micro Skills and Unlocking Macro Careers' using NLP and resume/code parsing.
  3. Dashboards: Hospital Management (Power BI), Employee Performance (Excel), Smoking Behavior & Health Indicators (Power BI).
  4. Other: Gesture-controlled virtual mouse (OpenCV & MediaPipe), Brain Tumor MRI classification.
- Tone: Professional, enthusiastic, data-driven, polite, and confident.
- Style: Always answer directly based on the provided context. If asked about something outside your expertise, politely mention your focus areas and invite them to connect via email (Praneeth.dupukuntla@gmail.com).
"""

SUGGESTED_PROMPTS = [
    "Tell me about your ByteLife health monitoring project.",
    "What Power BI, DAX, and analytics tools do you specialize in?",
    "Where did you publish your research paper and what was it about?",
    "What is your educational background and where are you located?",
    "What dashboards have you built for business and healthcare?",
    "How can I get in touch with you for interviews or collaborations?"
]

def synthesize_first_person_response(query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
    """
    Intelligent first-person conversational synthesis using semantic matching
    and retrieved knowledge chunks based on the currently active person profile.
    """
    q_lower = query.lower()
    prof = get_current_profile()
    name = prof.get("name", "Pranith Kumar Dupuguntla")
    role = prof.get("role", "Data Analyst")
    location = prof.get("location", "Hyderabad, India")
    education = prof.get("education", "B.Tech in CSE (Data Science), ACE Engineering College")
    skills = prof.get("skills", ["Power BI", "DAX", "Python", "SQL", "Excel"])
    email = prof.get("email", "Praneeth.dupukuntla@gmail.com")
    phone = prof.get("phone", "+91 6300905921")
    bio = prof.get("bio", "")
    
    # 1. Greetings / Introduction
    if re.search(r"\b(hi|hello|hey|greetings|who are you|introduce yourself|tell me about yourself)\b", q_lower) and len(query.split()) <= 6:
        skills_str = ", ".join(f"**{s}**" for s in skills[:5])
        return (
            f"Hello! I am **{name}**, a passionate **{role}** based in {location}.\n\n"
            f"{bio}\n\n"
            f"My technical toolkit centers around {skills_str}. "
            f"Feel free to ask me about my major projects, research, technical skills, or experience!"
        )

    # 2. ByteLife Project Queries
    if any(k in q_lower for k in ["bytelife", "byte life", "elderly", "aging population", "health monitor", "vitals", "random forest", "caregiver", "caretaker"]):
        resp = (
            "### 💓 Early Detection & Intervention for the Aging Population (ByteLife)\n\n"
            f"I co-authored and engineered **ByteLife**, an end-to-end telemetry and emergency dispatch platform "
            "specifically designed for elderly individuals living independently.\n\n"
            "**Key Architectural Highlights**:\n"
            "- **Physiological Telemetry**: Captures 5 vital parameters in real time: Heart Rate (bpm), Systolic & Diastolic Blood Pressure (mmHg), Oxygen Saturation (SpO₂ in %), and Body Temperature (°F).\n"
            "- **Dual-Layer Intelligence**: Combines a **Random Forest Classifier (99.78% accuracy)** with a deterministic **Clinical Rule-Based Failsafe Override** (e.g., promoting patients immediately to *Critical* if SpO₂ drops below 90% or Systolic BP exceeds 180 mmHg).\n"
            "- **Automated Alerting**: Instantly dispatches rich HTML emails to family caretakers with patient vitals, deviation flags, and actionable first-aid / OTC medicine guidance.\n"
            "- **Tech Stack**: Python, Flask, Scikit-Learn, Pandas, JavaScript, HTML5/CSS3, and SMTP."
        )
        return resp

    # 3. Research Paper Queries
    if any(k in q_lower for k in ["research", "paper", "ijirset", "publication", "micro skills", "macro careers", "published", "journal"]):
        resp = (
            "### 📄 Published Research in IJIRSET (March 2026)\n\n"
            "I co-authored a peer-reviewed research paper titled **\"Detecting Micro Skills and Unlocking Macro Careers\"**, "
            "published in the *International Journal of Innovative Research in Science, Engineering and Technology* (IJIRSET, Vol. 15, Issue 3, Impact Factor: 8.699, DOI: 10.15680/IJIRSET.2026.1503130).\n\n"
            "**Core Contribution & Methodology**:\n"
            "- Solved the fundamental limitations of traditional keyword-based ATS resume filters.\n"
            "- Built an AI-driven platform using **Natural Language Processing (NLP)** and Machine Learning to parse resumes and extract verified micro-skills from candidate coding repositories (GitHub, LeetCode).\n"
            "- Performs automated skill-gap analysis, generates ATS-optimized resume recommendations, and charts personalized upskilling roadmaps mapped to industry roles."
        )
        return resp

    # 4. Skills Queries
    if any(k in q_lower for k in ["power bi", "dax", "excel", "power query", "tableau", "tools", "skills", "technologies", "sql", "python"]):
        skills_bullets = "\n".join(f"- **{s}**" for s in skills)
        return (
            f"### 🛠️ Technical Competencies & Tooling\n\n"
            f"My core toolkit as a **{role}** includes:\n\n"
            f"{skills_bullets}\n\n"
            f"I have applied these tools extensively across enterprise dashboard development, predictive analytics, ETL pipeline engineering, and statistical modeling."
        )

    # 5. Dashboards & Projects Queries
    if any(k in q_lower for k in ["dashboard", "projects", "hospital", "employee performance", "smoking", "mouse", "tumor"]):
        projects = prof.get("projects", [])
        if projects:
            proj_lines = []
            for idx, p in enumerate(projects, 1):
                if isinstance(p, dict):
                    tech_str = f" (Tech: {', '.join(p.get('tech', []))})" if p.get("tech") else ""
                    proj_lines.append(f"{idx}. **{p.get('title')}**{tech_str}:\n   - {p.get('description')}")
                elif isinstance(p, str):
                    proj_lines.append(f"{idx}. {p}")
            return "### 📊 Key Analytics Dashboards & Projects I've Built\n\n" + "\n\n".join(proj_lines)

    # 6. Education & Location Queries
    if any(k in q_lower for k in ["education", "college", "degree", "btech", "b.tech", "diploma", "where do you live", "location", "hyderabad", "jntuh"]):
        return (
            f"### 🎓 Education & Background\n\n"
            f"- **Educational Background**: {education}\n"
            f"- **Location**: {location}\n\n"
            f"My academic training emphasizes machine learning, statistical modeling, database systems, and end-to-end data analytics."
        )

    # 7. Contact & Roles Queries
    if any(k in q_lower for k in ["contact", "email", "phone", "hire", "roles", "interview", "reach", "resume", "github", "linkedin"]):
        roles_str = ", ".join(prof.get("target_roles", ["Data Analyst", "Business Analyst"]))
        return (
            f"### 📬 Contact & Open Opportunities\n\n"
            f"I am actively interviewing for **{roles_str}** positions.\n\n"
            f"- **Name**: {name}\n"
            f"- **Email**: [{email}](mailto:{email})\n"
            f"- **Phone**: {phone}\n"
            f"- **Location**: {location}\n\n"
            f"I'd be glad to discuss how my skill set can deliver immediate value to your team!"
        )

    # 8. Dynamic RAG synthesis using retrieved chunks
    if retrieved_docs:
        top_chunk = retrieved_docs[0]["content"]
        source_title = retrieved_docs[0]["title"]
        clean_chunk = " ".join(top_chunk.split()[:160])
        return (
            f"Based on my official project records ({source_title}):\n\n"
            f"> \"{clean_chunk}...\"\n\n"
            f"In my work on this area, I focused on applying structured data engineering, predictive modeling, "
            f"and clear visualization to deliver reliable, production-ready results. "
            f"Would you like me to elaborate on the technical implementation details or the results we achieved?"
        )

    return (
        f"I'm {name}! While I don't have specific details on that exact question in my "
        f"current knowledge base, I can share in-depth information about my major projects, "
        f"technical skills ({', '.join(skills[:4])}), or educational background. "
        f"Feel free to ask or contact me directly at **{email}**!"
    )

def ask_digital_me(user_query: str) -> Dict[str, Any]:
    """
    Main entry point for querying Digital Pranith.
    Retrieves semantic context and produces a first-person persona response.
    """
    clean_query = user_query.strip()
    if not clean_query:
        return {
            "query": "",
            "response": "Please enter a question, and I'll be happy to answer it as Pranith!",
            "sources": [],
            "suggested_questions": SUGGESTED_PROMPTS[:3]
        }

    # 1. Semantic Retrieval
    retrieved = search_knowledge_base(clean_query, k=3)

    # 2. Check if an external LLM key is configured (Groq / Gemini / OpenAI)
    llm_response = None
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if groq_key:
        try:
            from langchain_groq import ChatGroq
            chat = ChatGroq(temperature=0.2, model_name="llama-3.3-70b-versatile", groq_api_key=groq_key)
            context_text = "\n\n".join([f"[{d['title']}]: {d['content']}" for d in retrieved])
            messages = [
                ("system", SYSTEM_PERSONA_PROMPT),
                ("user", f"Context:\n{context_text}\n\nUser Question: {clean_query}")
            ]
            res = chat.invoke(messages)
            llm_response = res.content
        except Exception as e:
            print(f"[!] Groq API call failed: {e}")

    elif gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PERSONA_PROMPT)
            context_text = "\n\n".join([f"[{d['title']}]: {d['content']}" for d in retrieved])
            prompt = f"Knowledge Context:\n{context_text}\n\nUser Query: {clean_query}"
            res = model.generate_content(prompt)
            llm_response = res.text
        except Exception as e:
            print(f"[!] Gemini API call failed: {e}")

    # Fallback to smart semantic synthesis if no external LLM configured
    final_text = llm_response if llm_response else synthesize_first_person_response(clean_query, retrieved)

    # Format citations
    sources_summary = []
    for doc in retrieved:
        sources_summary.append({
            "title": doc.get("title", doc.get("source", "Knowledge Base")),
            "source": doc.get("source", ""),
            "snippet": doc.get("content", "")[:180] + "..."
        })

    return {
        "query": clean_query,
        "response": final_text,
        "sources": sources_summary,
        "suggested_questions": [q for q in SUGGESTED_PROMPTS if q.lower() not in clean_query.lower()][:3]
    }

if __name__ == "__main__":
    test_q = "Tell me about your ByteLife health monitoring project and what ML model you used."
    ans = ask_digital_me(test_q)
    print("Query:", ans["query"])
    print("\nAnswer:\n", ans["response"])
    print("\nSources Retrieved:", len(ans["sources"]))

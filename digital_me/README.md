# 🌐 Digital Me: Personal AI Digital Twin
**Cost-Free, Offline-First Personal AI Digital Twin for Pranith Kumar Dupuguntla**

[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-00f0ff.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-0070f3.svg)](#)
[![RAG](https://img.shields.io/badge/RAG-ChromaDB%20%2B%20FastEmbed%20ONNX-7928ca.svg)](#)
[![LLM](https://img.shields.io/badge/LLM-Local%20Ollama%20(Llama%203)-00ff88.svg)](#)
[![TTS](https://img.shields.io/badge/Voice-Edge--TTS%20Neural-ff0055.svg)](#)

---

## 🚀 Overview

**Digital Me** is an end-to-end, cost-free, offline-first personal AI Digital Twin engineered specifically for **Pranith Kumar Dupuguntla**. It speaks strictly in the **first person ("I", "my", "me")**, answering technical interviews, recruiter inquiries, and project deep-dives grounded directly in Pranith's authentic academic documents, research publications, and data analytics portfolio.

### Key Architectural Pillars:
1. **Local Semantic RAG Engine**: ChromaDB persistent vector database powered by **ONNX-based FastEmbed (`BAAI/bge-small-en-v1.5`)** to eliminate Windows PyTorch DLL conflicts, paired with an instant offline lexical fallback.
2. **Local LLM Inference**: Integrated with local **Ollama** running **Llama 3** with strict first-person persona conditioning, plus an offline-first persona synthesizer fallback.
3. **Neural Text-to-Speech (TTS)**: **Edge-TTS** neural voice synthesis producing high-definition `.mp3` audio response streams with zero API subscription fees.
4. **Neon-Blue Cyberpunk Web Dashboard**: Single-page dark-mode UI with dynamic concentric avatar pulse frames and real-time audio waveform equalizer animations synchronized to voice playback.

---

## 📂 Project Directory Structure

```text
digital_me/
├── data/                               # Knowledge base source documents
│   ├── pranith_profile.json            # Structured persona specifications
│   ├── resume_summary.txt              # Resume credentials, tools & metrics
│   ├── personal_qa.txt                 # Personal Q&A and bio details
│   ├── projects_research.txt           # ByteLife & IJIRSET research summaries
│   ├── bytelife_report.txt             # Complete ByteLife mini-project report
│   └── microskills_paper.txt           # Published IJIRSET research paper
├── chroma_db/                          # Persistent ChromaDB vector storage (456 embeddings)
│   └── chroma.sqlite3
├── backend/                            # Modular Python backend architecture
│   ├── __init__.py
│   ├── rag_engine.py                   # ChromaDB + FastEmbed ONNX retrieval pipeline
│   ├── llm_chain.py                    # Ollama Llama 3 local inference & persona chain
│   ├── voice_synthesizer.py            # Edge-TTS neural speech engine & audio caching
│   ├── audio_cache/                    # Cached .mp3 synthesized voice files
│   └── app.py                          # Flask REST API + static frontend server
├── frontend/                           # Dark-mode neon-blue interactive dashboard
│   ├── index.html                      # Semantic single-page application shell
│   ├── styles.css                      # Cyberpunk neon-blue CSS & avatar animations
│   └── app.js                          # Audio playback sync & chat controller
├── requirements.txt                    # Python runtime dependencies
├── run_digital_me.bat                  # One-click Windows batch execution script
└── README.md                           # Documentation & architecture specifications
```

---

## ⚡ Quick Start Guide

### Option 1: One-Click Execution (Windows)
Double-click `run_digital_me.bat` in the project root or inside `digital_me/`. The script will:
- Check your Python environment.
- Verify required packages.
- Probe the local Ollama daemon.
- Launch the Flask server on `http://localhost:5000`.
- Automatically open your default web browser to the dashboard.

### Option 2: Manual Terminal Startup
```bash
# 1. Navigate to the project directory
cd digital_me

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Start local Ollama Llama 3 in a separate terminal:
ollama run llama3

# 4. Launch backend server
python backend/app.py
```
Open **[http://localhost:5000](http://localhost:5000)** in your browser.

---

## 📡 API Endpoints Specification

| Method | Endpoint | Description | Sample Request / Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | System diagnostics & status | Returns RAG, ChromaDB chunk count, and Ollama status |
| `POST` | `/api/chat` | Main conversational RAG query | `{"query": "Tell me about ByteLife", "synthesize_audio": true}` |
| `POST` | `/api/audio` | Direct text-to-speech generation | `{"text": "Hello world", "voice": "en-US-ChristopherNeural"}` |
| `GET` | `/api/audio/<filename>` | Stream generated MP3 audio | Returns `audio/mpeg` binary stream |
| `GET` | `/api/voices` | List available neural voices | Returns supported voice names and labels |
| `GET` | `/api/knowledge` | Knowledge base diagnostics | Returns count of files and vector index stats |

---

## 🎭 Persona Specifications

- **Name**: Pranith Kumar Dupuguntla
- **Current Role**: Data Analyst & Computer Science (Data Science) Student
- **College**: ACE Engineering College, Hyderabad (Affiliated with JNTUH)
- **Flagship Project**: **ByteLife** — Elderly health telemetry platform tracking 5 vital signs with Random Forest (99.78% accuracy) and clinical safety failsafes.
- **Published Research**: **IJIRSET (March 2026)** — *"Detecting Micro Skills and Unlocking Macro Careers"* (NLP-driven resume and code repository skill extractor).
- **Tooling**: Power BI, DAX, Advanced Excel, Python (Pandas, Scikit-learn), SQL, Tableau, OpenCV.
- **Contact**: `Praneeth.dupukuntla@gmail.com` | `+91 6300905921`

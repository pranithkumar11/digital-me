# 🛠️ Digital Me: Local Development Guide

Welcome to the local development environment for **Digital Me** (Pranith Kumar Dupuguntla's Personal AI Twin).

---

## ⚡ Active Local Development Features

Your system is currently equipped with **full live development mode**:
- **Flask Auto-Reloading (`Debug Mode: ON`)**: Any changes you save in `backend/app.py`, `rag_engine.py`, `llm_chain.py`, or `voice_synthesizer.py` automatically restart the server in <1 second.
- **Disabled Browser Caching (`SEND_FILE_MAX_AGE_DEFAULT = 0`)**: Any changes to `frontend/index.html`, `styles.css`, or `app.js` reflect immediately upon refreshing your browser tab (no hard cache clears needed).
- **One-Click Re-Indexing (`/api/reindex`)**: A dedicated **`[ 🔄 Re-Index KB ]`** button is right on the dashboard footer to instantly ingest new files added to `data/`.
- **Audio Cache Purging (`/api/dev/clear-audio`)**: Clean up cached response audio files during iteration.

---

## 🚀 Starting the Local Dev Server

### Option A: One-Click Launcher (Recommended)
Double-click [**`run_dev.bat`**](file:///C:/Users/prane/OneDrive/Desktop/digit_me%20doc/run_dev.bat) in the root workspace folder or in `digital_me/`.

### Option B: Terminal Command
```powershell
cd "digital_me\backend"
python app.py
```
Open your browser at: **[http://localhost:5000](http://localhost:5000)**

---

## 📂 How to Develop & Customize

### 1. Modifying the Knowledge Base (RAG)
1. Add any `.txt`, `.md`, or `.json` file to the [`digital_me/data/`](file:///C:/Users/prane/OneDrive/Desktop/digit_me%20doc/digital_me/data) folder.
2. In your browser dashboard, click **`[ 🔄 Re-Index KB ]`** on the bottom right of the chat bar.
3. Your new knowledge is immediately chunked and embedded into ChromaDB with FastEmbed ONNX!

### 2. Modifying the First-Person Persona & Prompts
- Edit [`digital_me/backend/llm_chain.py`](file:///C:/Users/prane/OneDrive/Desktop/digit_me%20doc/digital_me/backend/llm_chain.py).
- Locate `PRANITH_SYSTEM_PROMPT` to refine interview tone, response format, or career guidelines.
- Save the file — Flask will auto-reload instantaneously in your terminal!

### 3. Modifying the UI & Animations
- **HTML Shell**: [`digital_me/frontend/index.html`](file:///C:/Users/prane/OneDrive/Desktop/digit_me%20doc/digital_me/frontend/index.html)
- **Styling & Cyberpunk FX**: [`digital_me/frontend/styles.css`](file:///C:/Users/prane/OneDrive/Desktop/digit_me%20doc/digital_me/frontend/styles.css)
- **Audio & Avatar Interaction**: [`digital_me/frontend/app.js`](file:///C:/Users/prane/OneDrive/Desktop/digit_me%20doc/digital_me/frontend/app.js)
- Simply make your edits, save, and hit `F5` in your browser!

### 4. Running with Local Ollama (Llama 3)
In a separate PowerShell window, run:
```powershell
ollama run llama3
```
Digital Me automatically detects Ollama running on `http://localhost:11434` and switches from persona synthesis to live local Llama 3 neural inference!

### 5. Running the Automated Test Suite
```powershell
cd "digital_me"
python test_digital_me.py
```
All 15 integration and unit tests run in under 1 second.

"""
app.py - Main Flask REST API for Digital Me
Features:
- CORS enabled for cross-origin frontend interactions
- Endpoints: /health, /api/chat, /api/audio, /api/audio/<filename>, /api/voices, /api/knowledge
- Serves the neon-blue interactive frontend directly on root URL (/)
- Clean, robust error handling and response metadata
"""

import os
import sys
import time
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

# Import modular backend components
from rag_engine import get_rag_engine
from llm_chain import get_llm_chain
from voice_synthesizer import get_voice_synthesizer

# Initialize Flask application (Defaults to local development mode)
DEBUG_MODE = os.getenv("PRODUCTION", "false").lower() not in ("true", "1", "yes")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
CORS(app, resources={r"/*": {"origins": "*"}})

if DEBUG_MODE:
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

@app.after_request
def add_header(response):
    if DEBUG_MODE:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Global component instances
rag_engine = get_rag_engine()
llm_chain = get_llm_chain()
voice_synthesizer = get_voice_synthesizer()


# ==========================================
# Frontend Routes
# ==========================================

@app.route("/")
def serve_index():
    """Serve the single-page application dashboard."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static_file(path):
    """Serve CSS, JS, and image static assets from frontend directory."""
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


# ==========================================
# API Routes
# ==========================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check diagnostic endpoint."""
    ollama_info = llm_chain.check_ollama_status()
    kb_info = rag_engine.get_kb_stats()
    
    return jsonify({
        "status": "healthy",
        "service": "Digital Me - Personal AI Digital Twin",
        "persona": "Pranith Kumar Dupuguntla",
        "architecture": {
            "embeddings": kb_info.get("embedding_model"),
            "vector_store": "ChromaDB (FastEmbed ONNX)",
            "llm_engine": "Ollama / Llama 3",
            "voice_synthesis": "Edge-TTS Neural Voice"
        },
        "diagnostics": {
            "ollama": ollama_info,
            "knowledge_base": kb_info
        },
        "server_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }), 200


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """
    Main conversational endpoint:
    1. Retrieves relevant documents from ChromaDB / Knowledge Base via RAG
    2. Passes persona prompt + retrieved context + query to Ollama Llama 3
    3. Synthesizes Edge-TTS audio response file (.mp3)
    4. Returns JSON with text response, source citations, audio URL, and metadata
    """
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    synthesize_audio = data.get("synthesize_audio", True)
    voice = data.get("voice", None)
    top_k = int(data.get("top_k", 4))

    if not query:
        return jsonify({
            "error": "Query string is required in the request payload.",
            "success": False
        }), 400

    start_time = time.time()

    # 1. RAG Retrieval
    try:
        retrieved_docs = rag_engine.query_similar(query, top_k=top_k)
    except Exception as e:
        print(f"[!] RAG retrieval warning: {e}")
        retrieved_docs = []

    # 2. LLM First-Person Persona Generation
    llm_result = llm_chain.generate_response(query, retrieved_docs)
    response_text = llm_result.get("response", "")

    # 3. Text-to-Speech Synthesis
    audio_info = None
    if synthesize_audio and response_text:
        try:
            audio_info = voice_synthesizer.synthesize(response_text, voice=voice)
        except Exception as e:
            print(f"[!] Speech synthesis warning: {e}")
            audio_info = {"success": False, "error": str(e), "audio_url": None}

    total_latency_ms = int((time.time() - start_time) * 1000)

    return jsonify({
        "success": True,
        "query": query,
        "response": response_text,
        "sources": llm_result.get("sources", []),
        "audio": audio_info,
        "audio_url": audio_info.get("audio_url") if audio_info else None,
        "audio_filename": audio_info.get("filename") if audio_info else None,
        "voice": audio_info.get("voice") if audio_info else voice_synthesizer.default_voice,
        "engine": llm_result.get("engine", "unknown"),
        "model": llm_result.get("model", "llama3"),
        "latency_ms": total_latency_ms,
        "suggested_questions": llm_result.get("suggested_questions", [])
    }), 200


@app.route("/api/audio", methods=["POST"])
def synthesize_custom_audio():
    """Standalone TTS endpoint to generate audio for arbitrary text."""
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    voice = data.get("voice", None)

    if not text:
        return jsonify({"error": "Text is required for audio synthesis.", "success": False}), 400

    result = voice_synthesizer.synthesize(text, voice=voice)
    status_code = 200 if result.get("success") else 500
    return jsonify(result), status_code


@app.route("/api/audio/<filename>", methods=["GET"])
def stream_audio(filename):
    """Stream generated MP3 audio files with proper MIME type."""
    file_path = voice_synthesizer.get_audio_path(filename)
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": f"Audio file '{filename}' not found."}), 404

    return send_file(
        file_path,
        mimetype="audio/mpeg",
        as_attachment=False,
        download_name=filename
    )


@app.route("/api/voices", methods=["GET"])
def list_voices():
    """List all supported neural voices."""
    return jsonify({
        "default": voice_synthesizer.default_voice,
        "voices": voice_synthesizer.list_voices()
    }), 200


@app.route("/api/knowledge", methods=["GET"])
def get_knowledge_base_info():
    """Diagnostic knowledge base metadata."""
    stats = rag_engine.get_kb_stats()
    return jsonify(stats), 200


@app.route("/api/reindex", methods=["POST"])
def reindex_knowledge_base():
    """Development endpoint: re-ingest and re-index all documents from data/ directory."""
    try:
        count = rag_engine.ingest_documents(force_reindex=True)
        return jsonify({
            "success": True,
            "message": f"Successfully re-indexed {count} knowledge chunks into ChromaDB.",
            "chunks_indexed": count
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/dev/clear-audio", methods=["POST"])
def clear_audio_cache():
    """Development endpoint: purge cached .mp3 audio files."""
    try:
        import glob
        files = glob.glob(os.path.join(AUDIO_CACHE_DIR, "*.mp3"))
        for f in files:
            try:
                os.remove(f)
            except Exception:
                pass
        return jsonify({"success": True, "deleted_count": len(files)}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"\n=========================================================")
    print(f"  DIGITAL ME - Pranith Kumar Dupuguntla's Digital Twin   ")
    print(f"  Mode: {'DEVELOPMENT (Auto-Reload ON)' if DEBUG_MODE else 'PRODUCTION'} ")
    print(f"  Server URL: http://localhost:{port}                    ")
    print(f"  Health Check: http://localhost:{port}/health           ")
    print(f"=========================================================\n")
    app.run(host="0.0.0.0", port=port, debug=DEBUG_MODE)

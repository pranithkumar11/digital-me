"""
test_digital_me.py - Comprehensive Unit & Integration Test Suite for Digital Me
Verifies:
1. RAG Engine retrieval and knowledge base stats
2. LLM First-Person chain persona generation
3. Voice Synthesizer text normalization & voice catalog
4. Flask REST API endpoints (/health, /api/chat, /api/voices, /api/knowledge, /)
"""

import os
import sys
import pytest

# Ensure digital_me/backend is on python path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(TEST_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from rag_engine import get_rag_engine
from llm_chain import get_llm_chain
from voice_synthesizer import get_voice_synthesizer, clean_text_for_speech
from app import app


@pytest.fixture
def api_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ==========================================
# 1. RAG Engine Tests
# ==========================================

def test_rag_stats():
    rag = get_rag_engine()
    stats = rag.get_kb_stats()
    assert stats["status"] == "ready"
    assert stats["document_files_count"] >= 6
    assert stats["total_indexed_chunks"] == 456
    assert stats["embedding_model"] == "BAAI/bge-small-en-v1.5"


def test_rag_retrieval_bytelife():
    rag = get_rag_engine()
    results = rag.query_similar("Tell me about the ByteLife health monitoring project", top_k=2)
    assert len(results) > 0
    assert any("bytelife" in r["title"].lower() or "bytelife" in r["content"].lower() for r in results)


def test_rag_retrieval_research_paper():
    rag = get_rag_engine()
    results = rag.query_similar("What was the IJIRSET published paper about?", top_k=2)
    assert len(results) > 0
    assert any("paper" in r["title"].lower() or "microskills" in r["source"].lower() or "paper" in r["content"].lower() for r in results)


# ==========================================
# 2. LLM Chain Tests
# ==========================================

def test_llm_status_check():
    llm = get_llm_chain()
    status = llm.check_ollama_status()
    assert "online" in status
    assert status["target_model"] == "llama3"


def test_llm_first_person_greeting():
    llm = get_llm_chain()
    res = llm.generate_response("Hello, who are you?", [])
    text = res["response"]
    assert "Pranith Kumar Dupuguntla" in text
    assert any(term in text for term in ["I am", "I specialize", "my", "Data Analyst"])


def test_llm_bytelife_persona():
    llm = get_llm_chain()
    res = llm.generate_response("What is ByteLife and what machine learning model did you use?", [])
    text = res["response"]
    assert "ByteLife" in text
    assert "Random Forest" in text
    assert "99.78%" in text


def test_llm_contact_persona():
    llm = get_llm_chain()
    res = llm.generate_response("How can I contact or hire you for Data Analyst roles?", [])
    text = res["response"]
    assert "Praneeth.dupukuntla@gmail.com" in text
    assert "+91 6300905921" in text


# ==========================================
# 3. Voice Synthesizer Tests
# ==========================================

def test_voice_text_cleansing():
    raw_markdown = "### Hello! **I am Pranith**. Visit [my website](https://example.com) `code`. \n\n- Point 1"
    cleaned = clean_text_for_speech(raw_markdown)
    assert "###" not in cleaned
    assert "**" not in cleaned
    assert "`" not in cleaned
    assert "https://" not in cleaned
    assert "Hello! I am Pranith. Visit my website code. Point 1" in cleaned


def test_voice_catalog():
    synth = get_voice_synthesizer()
    voices = synth.list_voices()
    assert "en-US-ChristopherNeural" in voices
    assert "en-IN-PrabhatNeural" in voices


# ==========================================
# 4. REST API Endpoint Tests
# ==========================================

def test_health_endpoint(api_client):
    res = api_client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["persona"] == "Pranith Kumar Dupuguntla"
    assert data["architecture"]["embeddings"] == "BAAI/bge-small-en-v1.5"


def test_chat_endpoint_valid(api_client):
    res = api_client.post("/api/chat", json={
        "query": "What Power BI and DAX skills do you have?",
        "synthesize_audio": False
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "Power BI" in data["response"]
    assert len(data["suggested_questions"]) > 0


def test_chat_endpoint_empty_query(api_client):
    res = api_client.post("/api/chat", json={"query": ""})
    assert res.status_code == 400


def test_voices_endpoint(api_client):
    res = api_client.get("/api/voices")
    assert res.status_code == 200
    data = res.get_json()
    assert "default" in data
    assert "voices" in data


def test_knowledge_endpoint(api_client):
    res = api_client.get("/api/knowledge")
    assert res.status_code == 200
    data = res.get_json()
    assert data["document_files_count"] >= 6
    assert data["total_indexed_chunks"] == 456


def test_frontend_serving(api_client):
    res = api_client.get("/")
    assert res.status_code == 200
    assert "Digital Me" in res.data.decode("utf-8")

    css_res = api_client.get("/styles.css")
    assert css_res.status_code == 200
    assert "--neon-blue" in css_res.data.decode("utf-8")

    js_res = api_client.get("/app.js")
    assert js_res.status_code == 200
    assert "global-audio-stream" in js_res.data.decode("utf-8")


if __name__ == "__main__":
    pytest.main(["-v", __file__])

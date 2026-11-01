"""
rag_engine.py - Retrieval-Augmented Generation Engine for Digital Me
Features:
- ChromaDB vector store persistence
- ONNX-based FastEmbed (BAAI/bge-small-en-v1.5) without PyTorch DLL dependencies
- Robust offline-first fallback keyword search
- Dynamic document ingestion & chunking
"""

import os
import sys
import glob
import json
import re
from typing import List, Dict, Any, Optional

# Ensure UTF-8 standard output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
CHROMA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "chroma_db"))

# Document metadata definitions
DOC_METADATA_MAP = {
    "personal_qa.txt": {
        "title": "Personal Background & Q&A Knowledge Base",
        "category": "personal_bio"
    },
    "resume_summary.txt": {
        "title": "Resume & Professional Qualifications",
        "category": "resume"
    },
    "projects_research.txt": {
        "title": "Major Projects & Academic Research",
        "category": "projects"
    },
    "bytelife_report.txt": {
        "title": "ByteLife Health Telemetry & ML System Report",
        "category": "research_report"
    },
    "microskills_paper.txt": {
        "title": "IJIRSET Paper: Micro Skills & Macro Careers",
        "category": "published_paper"
    },
    "pranith_profile.json": {
        "title": "Structured Profile Specification",
        "category": "profile"
    }
}


def _is_network_available(host="huggingface.co", port=443, timeout=1.0) -> bool:
    """Quick non-blocking check to verify if remote model repository is reachable."""
    import socket
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False


class RAGEngine:
    def __init__(self, data_dir: str = DATA_DIR, chroma_dir: str = CHROMA_DIR):
        self.data_dir = data_dir
        self.chroma_dir = chroma_dir
        self.embedding_model_name = "BAAI/bge-small-en-v1.5"
        self.embeddings = None
        self.vectorstore = None
        self._init_engine()

    def _init_engine(self):
        """Initialize FastEmbed and ChromaDB vectorstore with instantaneous offline fallback."""
        if _is_network_available():
            try:
                from langchain_community.embeddings import FastEmbedEmbeddings
                print(f"[*] Initializing FastEmbedEmbeddings ({self.embedding_model_name})...")
                # FastEmbed uses local ONNX runtime avoiding PyTorch DLL issues
                self.embeddings = FastEmbedEmbeddings(model_name=self.embedding_model_name)
            except Exception as e:
                print(f"[!] FastEmbed initialization notice: {e}")
                self.embeddings = None
        else:
            print("[*] Offline-first mode active: Network unreachable, using high-speed local lexical & token index.")

        if self.embeddings and os.path.exists(self.chroma_dir):
            try:
                from langchain_chroma import Chroma
                self.vectorstore = Chroma(
                    persist_directory=self.chroma_dir,
                    embedding_function=self.embeddings,
                    collection_name="langchain"
                )
                print(f"[OK] ChromaDB vectorstore loaded from {self.chroma_dir}")
            except Exception as e:
                print(f"[!] ChromaDB load notice: {e}")
                self.vectorstore = None

    def ingest_documents(self, force_reindex: bool = False) -> int:
        """Read documents from data directory, split into chunks, and store in ChromaDB."""
        if not self.embeddings:
            print("[!] Embeddings not available; skipping vector ingestion.")
            return 0

        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_core.documents import Document
        from langchain_chroma import Chroma

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=80,
            separators=["\n\n--- [Page", "\n\n", "\n", ". ", " ", ""]
        )

        all_docs: List[Document] = []
        files = glob.glob(os.path.join(self.data_dir, "*.*"))

        for fpath in files:
            fname = os.path.basename(fpath)
            meta = DOC_METADATA_MAP.get(fname, {"title": fname, "category": "general"})

            if fname.endswith(".txt") or fname.endswith(".md"):
                try:
                    with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                        text = f.read()
                    chunks = splitter.split_text(text)
                    for i, chunk in enumerate(chunks):
                        all_docs.append(Document(
                            page_content=chunk.strip(),
                            metadata={
                                "source": fname,
                                "title": meta["title"],
                                "category": meta["category"],
                                "chunk_id": f"{fname}_chunk_{i}"
                            }
                        ))
                except Exception as e:
                    print(f"[!] Error processing {fname}: {e}")

            elif fname.endswith(".json"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    json_text = json.dumps(data, indent=2)
                    chunks = splitter.split_text(json_text)
                    for i, chunk in enumerate(chunks):
                        all_docs.append(Document(
                            page_content=chunk.strip(),
                            metadata={
                                "source": fname,
                                "title": meta["title"],
                                "category": meta["category"],
                                "chunk_id": f"{fname}_json_{i}"
                            }
                        ))
                except Exception as e:
                    print(f"[!] Error reading JSON {fname}: {e}")

        if not all_docs:
            print("[!] No documents found to index.")
            return 0

        print(f"[*] Indexing {len(all_docs)} chunks into ChromaDB at {self.chroma_dir}...")
        self.vectorstore = Chroma.from_documents(
            documents=all_docs,
            embedding=self.embeddings,
            persist_directory=self.chroma_dir,
            collection_name="langchain"
        )
        print(f"[OK] Ingested and persisted {len(all_docs)} chunks successfully.")
        return len(all_docs)

    def query_similar(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant knowledge snippets.
        Attempts ChromaDB semantic search first, with high-fidelity keyword fallback.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        # 1. Try ChromaDB semantic vector search
        if self.vectorstore:
            try:
                docs = self.vectorstore.similarity_search(clean_query, k=top_k)
                if docs:
                    return [
                        {
                            "content": d.page_content,
                            "source": d.metadata.get("source", "Knowledge Base"),
                            "title": d.metadata.get("title", d.metadata.get("source", "Document")),
                            "category": d.metadata.get("category", "general"),
                            "method": "chroma_vector_similarity"
                        }
                        for d in docs
                    ]
            except Exception as e:
                print(f"[!] Chroma vector search exception: {e}. Falling back to keyword search.")

        # 2. Resilient Keyword / BM25-style search fallback
        return self._keyword_search_fallback(clean_query, top_k)

    def _keyword_search_fallback(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Searches documents locally using token overlap and frequency scoring."""
        results = []
        tokens = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
        if not tokens or not os.path.exists(self.data_dir):
            return results

        txt_files = glob.glob(os.path.join(self.data_dir, "*.*"))
        for fpath in txt_files:
            fname = os.path.basename(fpath)
            meta = DOC_METADATA_MAP.get(fname, {"title": fname, "category": "general"})

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
            except Exception:
                continue

            content_lower = content.lower()
            score = 0
            best_pos = -1

            for tok in tokens:
                matches = [m.start() for m in re.finditer(re.escape(tok), content_lower)]
                score += len(matches) * (3 if len(tok) > 4 else 1)
                if matches and best_pos == -1:
                    best_pos = matches[0]

            if score > 0:
                pos = max(0, best_pos - 80) if best_pos != -1 else 0
                snippet = content[pos:pos + 500].replace("\n", " ").strip()
                results.append({
                    "content": snippet,
                    "source": fname,
                    "title": meta.get("title", fname),
                    "category": meta.get("category", "general"),
                    "score": score,
                    "method": "offline_keyword_match"
                })

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

    def get_kb_stats(self) -> Dict[str, Any]:
        """Return diagnostic statistics about the knowledge base and vector store."""
        doc_count = len(glob.glob(os.path.join(self.data_dir, "*.*")))
        vectorstore_active = self.vectorstore is not None
        embedding_active = self.embeddings is not None
        
        # Check SQLite record count if file exists
        sqlite_records = 0
        sqlite_file = os.path.join(self.chroma_dir, "chroma.sqlite3")
        if os.path.exists(sqlite_file):
            try:
                import sqlite3
                conn = sqlite3.connect(sqlite_file)
                cur = conn.cursor()
                cur.execute("SELECT count(*) FROM embeddings;")
                row = cur.fetchone()
                if row:
                    sqlite_records = row[0]
                conn.close()
            except Exception:
                pass

        return {
            "status": "ready",
            "data_directory": self.data_dir,
            "document_files_count": doc_count,
            "chroma_persistence_dir": self.chroma_dir,
            "total_indexed_chunks": sqlite_records,
            "embedding_model": self.embedding_model_name,
            "vectorstore_ready": vectorstore_active,
            "embeddings_ready": embedding_active
        }


# Singleton instance
_rag_instance: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGEngine()
    return _rag_instance


if __name__ == "__main__":
    print("[*] Testing RAG Engine...")
    rag = get_rag_engine()
    stats = rag.get_kb_stats()
    print("KB Stats:", json.dumps(stats, indent=2))
    
    test_queries = [
        "Tell me about the ByteLife project",
        "What is the IJIRSET paper about?",
        "What are Pranith's Power BI skills?"
    ]
    for q in test_queries:
        print(f"\n--- Query: '{q}' ---")
        results = rag.query_similar(q, top_k=2)
        print(f"Found {len(results)} matches via {results[0]['method'] if results else 'none'}")
        if results:
            print(f"Title: {results[0]['title']}")
            print(f"Snippet: {results[0]['content'][:140]}...")

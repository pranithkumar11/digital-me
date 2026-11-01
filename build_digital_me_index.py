"""
build_digital_me_index.py
Ingests all knowledge base documents (including extracted ByteLife report and
Micro Skills research paper) and indexes them into a persistent ChromaDB vector store.
"""

import os
import sys
import glob

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_chroma import Chroma

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_digital_me")

FILE_METADATA = {
    "personal_qa.txt": {
        "title": "Personal Q&A Knowledge Base",
        "category": "qa_and_bio",
        "description": "Background, college, technical tools, primary languages, and career goals of Pranith Kumar Dupuguntla."
    },
    "resume_summary.txt": {
        "title": "Professional Resume Summary",
        "category": "resume",
        "description": "Data Analyst role details, Power BI, Advanced Excel, Python, and project metrics."
    },
    "projects_research.txt": {
        "title": "Projects & Research Summary",
        "category": "overview",
        "description": "High-level summary of ByteLife health telemetry and the IJIRSET research publication."
    },
    "bytelife_report.txt": {
        "title": "ByteLife Mini Project Report (Full 41 Pages)",
        "category": "academic_report",
        "description": "Complete documentation on Early Detection and Intervention for the Aging Population: architecture, Random Forest classifier, clinical rules, and emergency alerting."
    },
    "microskills_paper.txt": {
        "title": "IJIRSET Research Paper (Full 8 Pages)",
        "category": "research_publication",
        "description": "Published paper on Detecting Micro Skills and Unlocking Macro Careers: NLP resume parsing, LeetCode/GitHub extraction, skill gap analytics."
    }
}

def build_index():
    print(f"[*] Scanning Knowledge Base directory: {KB_DIR}")
    if not os.path.exists(KB_DIR):
        raise FileNotFoundError(f"Knowledge base directory '{KB_DIR}' does not exist.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=550,
        chunk_overlap=70,
        separators=["\n\n--- [Page", "\n\n", "\n", " ", ""]
    )

    all_docs: list[Document] = []
    
    txt_files = glob.glob(os.path.join(KB_DIR, "*.txt"))
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        meta_info = FILE_METADATA.get(filename, {
            "title": filename,
            "category": "general",
            "description": "Reference document"
        })

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()

        chunks = text_splitter.split_text(text)
        print(f" [+] {filename} ({len(text)} chars) -> {len(chunks)} chunks")

        for idx, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk.strip(),
                metadata={
                    "source": filename,
                    "title": meta_info["title"],
                    "category": meta_info["category"],
                    "chunk_id": f"{filename}_chunk_{idx}"
                }
            )
            all_docs.append(doc)

    print(f"\n[*] Total chunks prepared: {len(all_docs)}")
    print(f"[*] Initializing FastEmbedEmbeddings (BAAI/bge-small-en-v1.5)...")
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    print(f"[*] Building and persisting ChromaDB at: {PERSIST_DIR}")
    vectorstore = Chroma.from_documents(
        documents=all_docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    print("\n[OK] Vector store built successfully!")
    print("[*] Running verification query tests...")

    test_queries = [
        "What projects has Pranith built?",
        "Explain the ByteLife health monitoring methodology and ML classifier",
        "What is the IJIRSET research paper about?",
        "What Power BI and DAX skills does Pranith have?"
    ]

    for q in test_queries:
        print(f"\n--- Query: '{q}' ---")
        results = vectorstore.similarity_search(q, k=2)
        for i, res in enumerate(results, 1):
            src = res.metadata.get("source", "unknown")
            snippet = res.page_content.replace("\n", " ")[:150]
            print(f"  Result {i} [{src}]: {snippet}...")

    print("\n[OK] Indexing and verification complete!")
    return vectorstore

if __name__ == "__main__":
    build_index()

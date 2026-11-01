"""
update_notebook.py
Regenerates 'digital_me .ipynb' with the complete, functional RAG pipeline,
from document loading & FastEmbed chunking to persona-conditioned first-person generation.
"""

import json
import os

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Digital Me: AI Persona & RAG Digital Twin for Pranith Kumar Dupuguntla\n",
                "### Autonomous Knowledge Retrieval, Vector Store Embedding & Persona Generation\n",
                "\n",
                "This notebook implements an end-to-end **Retrieval-Augmented Generation (RAG)** pipeline representing **Pranith Kumar Dupuguntla**.\n",
                "It ingests personal records, resume summaries, the 41-page **ByteLife** mini-project report, and the published **IJIRSET** research paper, indexes them in a **ChromaDB** vector store using **FastEmbed** (`BAAI/bge-small-en-v1.5`), and responds to questions in the first person."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Step 1: Import Dependencies\n",
                "import os\n",
                "import sys\n",
                "import glob\n",
                "from langchain_text_splitters import RecursiveCharacterTextSplitter\n",
                "from langchain_core.documents import Document\n",
                "from langchain_community.embeddings import FastEmbedEmbeddings\n",
                "from langchain_chroma import Chroma\n",
                "\n",
                "print(\"All core LangChain, FastEmbed, and Chroma modules imported successfully!\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Step 2: Load Knowledge Base Documents\n",
                "We load all 5 foundational documents:\n",
                "1. `personal_qa.txt`: Personal Q&A, education, and career aspirations.\n",
                "2. `resume_summary.txt`: Power BI, Excel, and analytics competencies.\n",
                "3. `projects_research.txt`: High-level summary of academic accomplishments.\n",
                "4. `bytelife_report.txt`: Full 41-page mini project report (Random Forest, clinical safety rules, telemetry).\n",
                "5. `microskills_paper.txt`: Full 8-page IJIRSET published research paper on AI resume & micro-skill extraction."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Step 2: Load and Inspect Documents\n",
                "KB_DIR = os.path.join(os.getcwd(), \"knowledge_base\")\n",
                "if not os.path.exists(KB_DIR):\n",
                "    KB_DIR = os.getcwd()\n",
                "\n",
                "documents = []\n",
                "txt_files = glob.glob(os.path.join(KB_DIR, \"*.txt\"))\n",
                "\n",
                "for fpath in txt_files:\n",
                "    fname = os.path.basename(fpath)\n",
                "    with open(fpath, \"r\", encoding=\"utf-8\", errors=\"replace\") as f:\n",
                "        content = f.read()\n",
                "        documents.append({\"source\": fname, \"content\": content})\n",
                "    print(f\"Loaded: {fname} ({len(content)} characters)\")\n",
                "\n",
                "print(f\"\\nSuccessfully loaded {len(documents)} knowledge base documents.\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Step 3: Text Chunking with RecursiveCharacterTextSplitter\n",
                "We split the source documents into semantic chunks with 550 characters and 70 overlap to preserve contextual continuity."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Step 3: Chunk Documents\n",
                "text_splitter = RecursiveCharacterTextSplitter(\n",
                "    chunk_size=550,\n",
                "    chunk_overlap=70,\n",
                "    separators=[\"\\n\\n--- [Page\", \"\\n\\n\", \"\\n\", \" \", \"\"]\n",
                ")\n",
                "\n",
                "all_chunks = []\n",
                "for doc in documents:\n",
                "    chunks = text_splitter.split_text(doc[\"content\"])\n",
                "    for i, chunk in enumerate(chunks):\n",
                "        all_chunks.append(Document(\n",
                "            page_content=chunk.strip(),\n",
                "            metadata={\n",
                "                \"source\": doc[\"source\"],\n",
                "                \"chunk_id\": f\"{doc['source']}_chunk_{i}\"\n",
                "            }\n",
                "        ))\n",
                "    print(f\"- {doc['source']}: {len(chunks)} chunks\")\n",
                "\n",
                "print(f\"\\nTotal chunks ready for vector embeddings: {len(all_chunks)}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Step 4: FastEmbed Embedding & Persistent ChromaDB Index\n",
                "We initialize FastEmbed (`BAAI/bge-small-en-v1.5`), which generates dense vector representations without PyTorch overhead or DLL issues on Windows."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Step 4: Initialize FastEmbed and ChromaDB\n",
                "embeddings = FastEmbedEmbeddings(model_name=\"BAAI/bge-small-en-v1.5\")\n",
                "PERSIST_DIR = os.path.join(os.getcwd(), \"chroma_digital_me\")\n",
                "\n",
                "vectorstore = Chroma.from_documents(\n",
                "    documents=all_chunks,\n",
                "    embedding=embeddings,\n",
                "    persist_directory=PERSIST_DIR\n",
                ")\n",
                "\n",
                "print(f\"Vector database successfully indexed and saved at: {PERSIST_DIR}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Step 5: Test Semantic Similarity Search"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Step 5: Semantic Retrieval Test\n",
                "test_queries = [\n",
                "    \"What projects has Pranith built?\",\n",
                "    \"Explain the Random Forest classifier and clinical overrides in ByteLife\",\n",
                "    \"What is the title and journal of Pranith's published research paper?\",\n",
                "    \"What Power BI and DAX skills does Pranith possess?\"\n",
                "]\n",
                "\n",
                "for q in test_queries:\n",
                "    print(f\"\\n=== Query: '{q}' ===\")\n",
                "    hits = vectorstore.similarity_search(q, k=2)\n",
                "    for idx, hit in enumerate(hits, 1):\n",
                "        snippet = hit.page_content.replace(\"\\n\", \" \")[:160]\n",
                "        print(f\"  [{idx}] ({hit.metadata.get('source')}): {snippet}...\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## Step 6: Persona System Prompt & Generation Engine\n",
                "We condition the model with a first-person persona system prompt so it speaks as Pranith Kumar Dupuguntla."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Step 6: Digital Me Persona Prompt and Synthesis Pipeline\n",
                "from digital_me_engine import ask_digital_me\n",
                "\n",
                "def chat_with_pranith(user_question: str):\n",
                "    \"\"\"Ask Digital Pranith a question and print the formatted first-person response.\"\"\"\n",
                "    result = ask_digital_me(user_question)\n",
                "    print(f\"User: {user_question}\\n\")\n",
                "    print(f\"Digital Pranith:\\n{result['response']}\\n\")\n",
                "    print(\"Retrieved Sources:\")\n",
                "    for s in result[\"sources\"]:\n",
                "        print(f\" - {s['title']} ({s['source']})\")\n",
                "    print(\"-\" * 60)\n",
                "    return result\n",
                "\n",
                "# Live Test 1: Project overview\n",
                "chat_with_pranith(\"Tell me about your ByteLife healthcare project and its machine learning model.\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Live Test 2: Research Publication\n",
                "chat_with_pranith(\"Where did you publish your research paper and what problem does it solve?\")"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Live Test 3: Technical Skills & Contact\n",
                "chat_with_pranith(\"What are your core technical skills in Power BI and how can I contact you?\")"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.13.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open("digital_me .ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=1)

print("Successfully regenerated digital_me .ipynb!")

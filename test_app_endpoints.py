"""
test_app_endpoints.py - Automated verification of the Digital Me web endpoints
"""

import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from app import app

def test_endpoints():
    print("[*] Initializing Flask test client...")
    client = app.test_client()

    # 1. Test suggested questions endpoint
    print("\n--- Test 1: GET /api/digital_me/suggested ---")
    res1 = client.get("/api/digital_me/suggested")
    assert res1.status_code == 200, f"Expected 200, got {res1.status_code}"
    data1 = res1.get_json()
    print("Name:", data1.get("name"))
    print("Role:", data1.get("role"))
    print("Suggested count:", len(data1.get("suggested_questions", [])))

    # 2. Test chat endpoint with ByteLife
    print("\n--- Test 2: POST /api/digital_me/chat (ByteLife Query) ---")
    res2 = client.post("/api/digital_me/chat", json={
        "query": "Tell me about your ByteLife project and how it helps the aging population."
    })
    assert res2.status_code == 200, f"Expected 200, got {res2.status_code}"
    data2 = res2.get_json()
    print("Query:", data2.get("query"))
    print("Response Snippet:", data2.get("response", "")[:180], "...")
    print("Sources count:", len(data2.get("sources", [])))

    # 3. Test chat endpoint with IJIRSET research paper
    print("\n--- Test 3: POST /api/digital_me/chat (Research Paper Query) ---")
    res3 = client.post("/api/digital_me/chat", json={
        "query": "Where did you publish your research paper and what is the methodology?"
    })
    assert res3.status_code == 200, f"Expected 200, got {res3.status_code}"
    data3 = res3.get_json()
    print("Query:", data3.get("query"))
    print("Response Snippet:", data3.get("response", "")[:180], "...")

    # 4. Test backward-compatible /api/query
    print("\n--- Test 4: POST /api/query (Legacy route) ---")
    res4 = client.post("/api/query", json={"query": "Power BI DAX"})
    assert res4.status_code == 200, f"Expected 200, got {res4.status_code}"
    data4 = res4.get_json()
    print("Legacy Query:", data4.get("query"))
    print("Results count:", data4.get("results_count"))

    print("\n[OK] All Digital Me web endpoints verified successfully!")

if __name__ == "__main__":
    test_endpoints()

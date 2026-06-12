#!/usr/bin/env python3
"""Test FastAPI with real Gemini 2.5 Flash API."""

import httpx
import json
import time

BASE_URL = "http://localhost:8001/api/tasks"

print("🧪 Testing FastAPI with REAL Gemini API (gemini-2.5-flash)\n")
print("=" * 70)

# Test 1: Health check
print("\n📡 Test 1: API Health Check")
try:
    r = httpx.get("http://localhost:8001/docs")
    print(f"✅ API is alive (Status: {r.status_code})")
except Exception as e:
    print(f"❌ API unreachable: {e}")
    exit(1)

# Test 2: Create task with real Gemini
print("\n🚀 Test 2: Create Task with Real Gemini API")
task_input = "What are the top 3 programming languages in 2026?"
try:
    r = httpx.post(BASE_URL, json={"task": task_input}, timeout=120.0)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        task = r.json()
        print(f"✅ Task created successfully!")
        print(f"  Thread ID: {task['thread_id'][:12]}...")
        print(f"  Status: {task['status']}")
        print(f"  Pending Nodes: {task['pending_nodes']}")
        
        # Show research output
        research = task['state'].get('research_output', '')
        if research:
            print(f"\n🔍 Research Output (first 300 chars):")
            print(f"  {research[:300]}...")
        
        # Show analysis output
        analysis = task['state'].get('analysis_output', '')
        if analysis:
            print(f"\n📊 Analysis Output (first 300 chars):")
            print(f"  {analysis[:300]}...")
            
        print(f"\n✅ REAL GEMINI API IS WORKING! 🎉")
    else:
        print(f"❌ Failed: {r.text[:300]}")
        
except Exception as e:
    print(f"❌ Error: {str(e)[:200]}")

print("\n" + "=" * 70)

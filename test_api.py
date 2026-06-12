"""
Manual API Test Script for Enterprise AI Automation API.
Tests all endpoints: health (docs), create task, get task, resume task.
"""
import httpx
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_docs():
    """Test 1: Verify Swagger docs are accessible."""
    separator("TEST 1: GET /docs (Swagger UI)")
    try:
        r = httpx.get(f"{BASE_URL}/docs")
        print(f"  Status Code: {r.status_code}")
        print(f"  Content-Type: {r.headers.get('content-type', 'N/A')}")
        print(f"  Body length: {len(r.text)} chars")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        print("  ✅ PASSED")
        return True
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def test_openapi_schema():
    """Test 2: Verify OpenAPI JSON schema is accessible."""
    separator("TEST 2: GET /openapi.json (API Schema)")
    try:
        r = httpx.get(f"{BASE_URL}/openapi.json")
        print(f"  Status Code: {r.status_code}")
        data = r.json()
        print(f"  API Title: {data.get('info', {}).get('title', 'N/A')}")
        print(f"  API Version: {data.get('info', {}).get('version', 'N/A')}")
        paths = list(data.get("paths", {}).keys())
        print(f"  Endpoints: {paths}")
        assert r.status_code == 200
        print("  ✅ PASSED")
        return True
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def test_create_task():
    """Test 3: POST /api/tasks - Create a new task."""
    separator("TEST 3: POST /api/tasks (Create Task)")
    try:
        payload = {"task": "Check competitor pricing for ticket management SaaS."}
        print(f"  Payload: {json.dumps(payload)}")
        r = httpx.post(f"{BASE_URL}/api/tasks", json=payload, timeout=60.0)
        print(f"  Status Code: {r.status_code}")
        data = r.json()
        print(f"  Response: {json.dumps(data, indent=2)}")
        assert r.status_code == 200, f"Expected 200, got {r.status_code}"
        assert "thread_id" in data, "Missing thread_id in response"
        assert "status" in data, "Missing status in response"
        print(f"  Thread ID: {data['thread_id']}")
        print(f"  Task Status: {data['status']}")
        print(f"  Pending Nodes: {data.get('pending_nodes', [])}")
        print("  ✅ PASSED")
        return data
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return None

def test_get_task(thread_id):
    """Test 4: GET /api/tasks/{thread_id} - Retrieve task status."""
    separator(f"TEST 4: GET /api/tasks/{thread_id[:8]}... (Get Task Status)")
    try:
        r = httpx.get(f"{BASE_URL}/api/tasks/{thread_id}", timeout=30.0)
        print(f"  Status Code: {r.status_code}")
        data = r.json()
        print(f"  Thread ID: {data.get('thread_id', 'N/A')}")
        print(f"  Status: {data.get('status', 'N/A')}")
        print(f"  Pending Nodes: {data.get('pending_nodes', [])}")
        state = data.get("state", {})
        print(f"  Critic Score: {state.get('critic_score', 'N/A')}")
        print(f"  Requires Human: {state.get('requires_human', 'N/A')}")
        print(f"  Research Output (first 200 chars): {state.get('research_output', '')[:200]}")
        print(f"  Analysis Output (first 200 chars): {state.get('analysis_output', '')[:200]}")
        assert r.status_code == 200
        print("  ✅ PASSED")
        return data
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return None

def test_get_nonexistent_task():
    """Test 5: GET /api/tasks/{bad_id} - Retrieve a non-existent task."""
    separator("TEST 5: GET /api/tasks/nonexistent-id (404 Test)")
    try:
        r = httpx.get(f"{BASE_URL}/api/tasks/nonexistent-thread-id", timeout=10.0)
        print(f"  Status Code: {r.status_code}")
        print(f"  Response: {r.text}")
        assert r.status_code == 404, f"Expected 404, got {r.status_code}"
        print("  ✅ PASSED (correctly returned 404)")
        return True
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

def test_resume_task(thread_id, approved=True, feedback=None):
    """Test 6/7: POST /api/tasks/{thread_id}/resume - Resume a paused task."""
    action = "APPROVE" if approved else "REJECT"
    separator(f"TEST: POST /api/tasks/{thread_id[:8]}../resume ({action})")
    try:
        payload = {"approved": approved}
        if feedback:
            payload["feedback"] = feedback
        print(f"  Payload: {json.dumps(payload)}")
        r = httpx.post(f"{BASE_URL}/api/tasks/{thread_id}/resume", json=payload, timeout=60.0)
        print(f"  Status Code: {r.status_code}")
        data = r.json()
        print(f"  Thread ID: {data.get('thread_id', 'N/A')}")
        print(f"  Status: {data.get('status', 'N/A')}")
        print(f"  Pending Nodes: {data.get('pending_nodes', [])}")
        state = data.get("state", {})
        print(f"  Actions Taken: {state.get('actions_taken', [])}")
        print(f"  Final Output (first 300 chars): {state.get('final_output', '')[:300]}")
        print(f"  Messages count: {len(state.get('messages', []))}")
        assert r.status_code == 200
        print("  ✅ PASSED")
        return data
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return None

def run_all_tests():
    print("\n" + "#"*60)
    print("  Enterprise AI Automation API - Manual Test Suite")
    print("#"*60)
    
    results = {}
    
    # Test 1: Docs
    results["docs"] = test_docs()
    
    # Test 2: OpenAPI schema
    results["openapi"] = test_openapi_schema()
    
    # Test 3: Create task
    task_data = test_create_task()
    results["create_task"] = task_data is not None
    
    if not task_data:
        print("\n\n⚠️  Cannot continue tests without a valid task. Aborting.")
        return results
    
    thread_id = task_data["thread_id"]
    status = task_data["status"]
    
    # Test 4: Get task status
    get_data = test_get_task(thread_id)
    results["get_task"] = get_data is not None
    
    # Test 5: Get nonexistent task (404)
    results["get_404"] = test_get_nonexistent_task()
    
    # Test 6: Resume task (approve) - only if paused
    if status == "paused":
        resume_data = test_resume_task(thread_id, approved=True)
        results["resume_approved"] = resume_data is not None
        
        # If it's still paused after the first resume, resume again
        if resume_data and resume_data.get("status") == "paused":
            resume_data2 = test_resume_task(thread_id, approved=True)
            results["resume_approved_2"] = resume_data2 is not None
    else:
        print(f"\n  ℹ️  Task status is '{status}', not 'paused'. Skipping resume test.")
        results["resume_approved"] = "SKIPPED"
    
    # Final status check
    separator("FINAL: Check task after all operations")
    final = test_get_task(thread_id)
    
    # Test 7: Create a second task and reject it
    separator("TEST 7: Create and REJECT a task")
    task2 = test_create_task()
    if task2 and task2.get("status") == "paused":
        reject_data = test_resume_task(
            task2["thread_id"], 
            approved=False, 
            feedback="Need more data on Gamma Solutions pricing before proceeding."
        )
        results["resume_rejected"] = reject_data is not None
    else:
        results["resume_rejected"] = "SKIPPED"
    
    # Summary
    separator("TEST SUMMARY")
    for test_name, result in results.items():
        if result is True:
            icon = "✅"
        elif result is False:
            icon = "❌"
        else:
            icon = "⏭️"
        print(f"  {icon} {test_name}: {result}")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v not in (True, False))
    print(f"\n  Total: {passed} passed, {failed} failed, {skipped} skipped")
    
    return results

if __name__ == "__main__":
    run_all_tests()

import requests
import time
import json
import os
from pathlib import Path

# API Endpoints
SOLVE_URL = "http://localhost:8000/solve"

# Topics from curriculum
TOPICS_FILE = Path("curriculum/topics.yaml")
import yaml

with open(TOPICS_FILE, "r", encoding="utf-8") as f:
    curriculum = yaml.safe_load(f)
    topics = curriculum.get("topics", [])

def test_topic(topic):
    print(f"Testing Topic {topic['id']}: {topic['name']}...")
    payload = {"problem": topic['name']}
    try:
        response = requests.post(SOLVE_URL, json=payload, timeout=60)
        if response.status_code == 200:
            job = response.json()
            task_id = job.get("task_id")
            print(f"  Job submitted: task_id={task_id}")
            return task_id
        else:
            print(f"  FAILED to submit (Status {response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"  Error: {e}")
        return None

def poll_task(task_id):
    status_url = f"http://localhost:8000/status/{task_id}"
    while True:
        try:
            resp = requests.get(status_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                if status == "completed":
                    print(f"  SUCCESS: {data.get('video_url')}")
                    return True, None
                elif status == "failed":
                    print(f"  FAILED: {data.get('info')}")
                    return False, data.get("info")
                else:
                    # 'processing' or 'queued'
                    print(f"  Status: {status}...", end="\r")
                    time.sleep(5)
            else:
                print(f"  Error polling: {resp.text}")
                return False, resp.text
        except Exception as e:
            print(f"  Polling error: {e}")
            return False, str(e)

results = []
# For testing the refactor, let's run a subset (e.g., first 5) or all if possible.
# Use first 10 for a robust sample.
for topic in topics[:50]:
    task_id = test_topic(topic)
    if task_id:
        success, error = poll_task(task_id)
        results.append({"id": topic["id"], "name": topic["name"], "success": success, "error": error})
    else:
        results.append({"id": topic["id"], "name": topic["name"], "success": False, "error": "Submission failed"})

# Output results table
print("\n" + "="*50)
print(f"{'ID':<4} | {'Topic':<40} | {'Status':<10}")
print("-" * 60)
for res in results:
    status = "SUCCESS" if res["success"] else "FAILED"
    print(f"{res['id']:<4} | {res['name'][:40]:<40} | {status}")
    if not res["success"]:
        print(f"     Error: {res['error']}")
print("="*50)

with open("stress_test_results.json", "w") as f:
    json.dump(results, f, indent=4)

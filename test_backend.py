import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_backend():
    print(f"Testing Backend at {BASE_URL}")

    problems = [
        "Graph x^2"
    ]

    for problem in problems:
        print(f"\n--- Testing Problem: '{problem}' ---")
        
        # Submit Problem
        payload = {"problem": problem}
        try:
            resp = requests.post(f"{BASE_URL}/solve", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                task_id = data.get("task_id")
                print(f"[PASS] Submission successful. Task ID: {task_id}")
            else:
                print(f"[FAIL] Submission failed: {resp.status_code} - {resp.text}")
                continue
        except Exception as e:
             print(f"[FAIL] Submission error: {e}")
             continue

        # Poll Status
        print(f"Polling status for task {task_id}...")
        for i in range(30):
            time.sleep(1)
            try:
                resp = requests.get(f"{BASE_URL}/status/{task_id}")
                data = resp.json()
                status = data.get("status")
                
                if status in ["completed", "failed"]:
                    print(f"Final Status: {status}")
                    if status == "completed":
                         print(f"Video URL: {data.get('video_url')}")
                    elif status == "failed":
                        print(f"Info: {data.get('info')}")
                    break
                
                if i % 5 == 0:
                    print(f"Status: {status}...")
            except Exception as e:
                print(f"Polling error: {e}")
                break


if __name__ == "__main__":
    test_backend()

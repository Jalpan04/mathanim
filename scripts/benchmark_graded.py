import requests
import time
import json
import sys

API_URL = "http://localhost:8000"

TEST_CASES = [
    {
        "level": "EASY",
        "prompt": "Graph y = x^2 with a blue curve.",
        "timeout": 120
    },
    {
        "level": "MEDIUM",
        "prompt": "Visualize a red circle of radius 2 turning into a square.",
        "timeout": 180
    },
    {
        "level": "HARD",
        "prompt": "Show the derivation of the quadratic formula visually.",
        "timeout": 240
    },
    {
        "level": "TOUGH",
        "prompt": "Create a 3D scene with a rotating sphere and axes.",
        "timeout": 300
    },
    {
        "level": "NIGHTMARE",
        "prompt": "Simulate a double pendulum with chaotic motion traces.",
        "timeout": 360
    }
]

def run_benchmark():
    results = []
    print(f"🚀 Starting Benchmark: {len(TEST_CASES)} Cases\n")

    for test in TEST_CASES:
        print(f"--- Level: {test['level']} ---")
        print(f"Prompt: {test['prompt']}")
        
        start_time = time.time()
        try:
            # 1. Submit
            resp = requests.post(f"{API_URL}/solve", json={"problem": test['prompt']})
            if resp.status_code != 200:
                print(f"❌ Submission Failed: {resp.text}")
                results.append({"level": test['level'], "status": "SUBMISSION_FAIL", "time": 0})
                continue
                
            task_id = resp.json()['task_id']
            print(f"Task ID: {task_id}")
            
            # 2. Poll
            elapsed = 0
            status = "processing"
            video_url = None
            
            while elapsed < test['timeout']:
                time.sleep(2)
                elapsed = time.time() - start_time
                
                status_resp = requests.get(f"{API_URL}/status/{task_id}")
                data = status_resp.json()
                status = data['status']
                
                if status == 'completed':
                    video_url = data['video_url']
                    break
                elif status == 'failed':
                    print(f"❌ Failed: {data.get('info')}")
                    break
                
                sys.stdout.write(f"\rStatus: {status} ({int(elapsed)}s)")
                sys.stdout.flush()
                
            print("") # Newline
            
            duration = round(time.time() - start_time, 2)
            
            if status == 'completed':
                print(f"✅ Success in {duration}s")
                results.append({"level": test['level'], "status": "PASS", "time": duration, "video": video_url})
            elif status == 'failed':
                results.append({"level": test['level'], "status": "FAIL", "time": duration})
            else:
                print(f"⏱️ Timed Out after {duration}s")
                results.append({"level": test['level'], "status": "TIMEOUT", "time": duration})

        except Exception as e:
            print(f"💥 Exception: {e}")
            results.append({"level": test['level'], "status": "ERROR", "time": 0})
            
        print("-" * 30)
        time.sleep(2) # Cooldown

    # Summary
    print("\n📊 BENCHMARK SUMMARY")
    print("=" * 40)
    print(f"{'Level':<10} | {'Status':<10} | {'Time (s)':<10}")
    print("-" * 40)
    for r in results:
        print(f"{r['level']:<10} | {r['status']:<10} | {r['time']:<10}")
    print("=" * 40)

if __name__ == "__main__":
    run_benchmark()

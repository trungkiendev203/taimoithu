import time
import requests
import json
import subprocess

API_URL = "http://localhost:8000/api/v1/batch"

urls_to_test = [
    "https://www.youtube.com/watch?v=jNQXAC9IVRw", # Normal
    "https://www.youtube.com/watch?v=LXb3EKWsInQ", # 1080p/4K needing merge
    "https://www.youtube.com/watch?v=mEdbJtU1Y2w", # Private/Unavailable
    "https://www.youtube.com/watch?v=deleted123",  # Deleted/Invalid
    "https://www.youtube.com/watch?v=BaW_jenozKc"  # Short
]

def run_test():
    print("--- POST /api/v1/batch/create ---")
    resp = requests.post(f"{API_URL}/create", json={"urls": urls_to_test})
    print("Response Status:", resp.status_code)
    data = resp.json()
    print("Response JSON:", json.dumps(data, indent=2))
    
    batch_id = data["data"]["batch_id"]
    print(f"\nBatch ID: {batch_id}")
    
    while True:
        status_resp = requests.get(f"{API_URL}/{batch_id}")
        status_data = status_resp.json()["data"]
        status = status_data["status"]
        print(f"Status: {status} | Completed: {status_data['completed_items']}/{status_data['total_items']}")
        if status in ["completed", "failed"]:
            print("\n--- Final GET /api/v1/batch/{batch_id} ---")
            print(json.dumps(status_data, indent=2))
            break
        time.sleep(5)
        
    print("\n--- Inspecting Redis Keys ---")
    result = subprocess.run(["docker-compose", "exec", "-T", "redis", "redis-cli", "hgetall", f"batch_job:{batch_id}"], capture_output=True, text=True)
    print("Metadata Hash:")
    print(result.stdout)
    
    result_items = subprocess.run(["docker-compose", "exec", "-T", "redis", "redis-cli", "hgetall", f"batch_job:{batch_id}:items"], capture_output=True, text=True)
    print("Items Hash:")
    print(result_items.stdout)

if __name__ == "__main__":
    run_test()

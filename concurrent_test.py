# concurrent_test.py - Concurrent User Test
import requests
import threading
import time
import json
from datetime import datetime

API_URL = "http://localhost:8000/query"

# Test questions
QUESTIONS = [
    "Agile Cevik yontem nedir?",
    "Yazilim muhendisligi nedir?",
    "monolotik yapi nedir?",
    "Hangi teknolojiler kullaniliyor?",
    "Güvenlik Açığı Nasıl Oluşur??",
]

results = []
all_test_results = []

def send_request(user_id, question):
    """Sends a single user request"""
    start = time.time()
    try:
        response = requests.post(API_URL, json={"question": question}, timeout=120)
        elapsed = time.time() - start
        data = response.json()
        answer = data.get("answer", "")
        results.append({
            "user": user_id,
            "question": question,
            "answer": answer,
            "status": response.status_code,
            "time": round(elapsed, 2),
            "success": True
        })
        print(f"✓ User {user_id}: {elapsed:.2f}s")
    except Exception as e:
        elapsed = time.time() - start
        results.append({
            "user": user_id,
            "question": question,
            "answer": "",
            "status": "error",
            "time": round(elapsed, 2),
            "success": False,
            "error": str(e)
        })
        print(f"✗ User {user_id}: ERROR - {e}")

def test_concurrent_users(num_users):
    """Tests specified number of concurrent users"""
    print(f"\n{'='*50}")
    print(f"TEST: {num_users} concurrent users")
    print(f"{'='*50}")
    
    results.clear()
    threads = []
    
    start_time = time.time()
    
    for i in range(num_users):
        question = QUESTIONS[i % len(QUESTIONS)]
        t = threading.Thread(target=send_request, args=(i+1, question))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    total_time = time.time() - start_time
    
    successful = sum(1 for r in results if r["success"])
    failed = num_users - successful
    avg_time = sum(r["time"] for r in results) / len(results) if results else 0
    
    print(f"\n--- RESULT ---")
    print(f"Total time: {total_time:.2f}s")
    print(f"Successful: {successful}/{num_users}")
    print(f"Failed: {failed}/{num_users}")
    print(f"Average response time: {avg_time:.2f}s")
    
    test_result = {
        "user_count": num_users,
        "total_time": round(total_time, 2),
        "successful": successful,
        "failed": failed,
        "avg_response_time": round(avg_time, 2),
        "details": list(results)
    }
    all_test_results.append(test_result)
    
    return successful == num_users

def save_results():
    """Saves results to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    report = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tests": all_test_results
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Results saved: {filename}")
    return filename

if __name__ == "__main__":
    print("="*50)
    print("CONCURRENT USER TEST")
    print("="*50)
    
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
        print("✓ Server is running\n")
    except:
        print("✗ Server is not running! First run 'python api_server.py'")
        exit(1)
    
    for num_users in [5, 10, 15]:
        test_concurrent_users(num_users)
        time.sleep(2)
    
    save_results()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED!")
    print("="*50)

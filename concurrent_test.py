"""
Concurrent Load Testing Script for Step 4: Scalability & Parallelism
Tests the system's ability to handle multiple simultaneous requests
"""

import requests
import concurrent.futures
import time
import statistics
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000/api"
NUM_CONCURRENT_USERS = 20
NUM_REQUESTS_PER_USER = 5


def send_text_grpc(user_id, request_num):
    """Send text message using gRPC endpoint"""
    try:
        start = time.perf_counter()
        response = requests.post(
            f"{BASE_URL}/send-text/",
            json={
                "sender": f"user{user_id}",
                "receiver": "server",
                "text": f"Hello World from user {user_id}, request {request_num}",
                "target_language": "fr"
            },
            timeout=10
        )
        end = time.perf_counter()
        
        return {
            "user_id": user_id,
            "request_num": request_num,
            "status": response.status_code,
            "time_ms": (end - start) * 1000,
            "method": "gRPC",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "user_id": user_id,
            "request_num": request_num,
            "status": 0,
            "time_ms": 0,
            "method": "gRPC",
            "success": False,
            "error": str(e)
        }


def send_text_rest(user_id, request_num):
    """Send text message using REST-only endpoint"""
    try:
        start = time.perf_counter()
        response = requests.post(
            f"{BASE_URL}/send-text-rest/",
            json={
                "sender": f"user{user_id}",
                "receiver": "server",
                "text": f"Hello World from user {user_id}, request {request_num}",
                "target_language": "fr"
            },
            timeout=10
        )
        end = time.perf_counter()
        
        return {
            "user_id": user_id,
            "request_num": request_num,
            "status": response.status_code,
            "time_ms": (end - start) * 1000,
            "method": "REST",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "user_id": user_id,
            "request_num": request_num,
            "status": 0,
            "time_ms": 0,
            "method": "REST",
            "success": False,
            "error": str(e)
        }


def send_audio_grpc(user_id, request_num):
    """Send audio message using gRPC endpoint"""
    try:
        start = time.perf_counter()
        response = requests.post(
            f"{BASE_URL}/send-audio/",
            json={
                "sender": f"user{user_id}",
                "receiver": "server",
                "audio": "SGVsbG8gV29ybGQgQXVkaW8gVGVzdA=="  # Base64 audio
            },
            timeout=10
        )
        end = time.perf_counter()
        
        return {
            "user_id": user_id,
            "request_num": request_num,
            "status": response.status_code,
            "time_ms": (end - start) * 1000,
            "method": "gRPC-Audio",
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "user_id": user_id,
            "request_num": request_num,
            "status": 0,
            "time_ms": 0,
            "method": "gRPC-Audio",
            "success": False,
            "error": str(e)
        }


def analyze_results(results, test_name):
    """Analyze and display test results"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\nTotal Requests: {len(results)}")
    print(f"Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    
    if successful:
        times = [r['time_ms'] for r in successful]
        print(f"\nResponse Time Statistics:")
        print(f"  Min:     {min(times):.2f} ms")
        print(f"  Max:     {max(times):.2f} ms")
        print(f"  Average: {statistics.mean(times):.2f} ms")
        print(f"  Median:  {statistics.median(times):.2f} ms")
        if len(times) > 1:
            print(f"  StdDev:  {statistics.stdev(times):.2f} ms")
        
        # Show sample of individual results
        print(f"\nSample Results (first 5):")
        for r in successful[:5]:
            print(f"  User {r['user_id']}, Req {r['request_num']}: {r['time_ms']:.2f} ms")
    
    if failed:
        print(f"\nFailed Requests:")
        for r in failed[:5]:  # Show first 5 failures
            error = r.get('error', 'Unknown error')
            print(f"  User {r['user_id']}, Req {r['request_num']}: {error}")
    
    print()


def test_concurrent_users_text_grpc():
    """Test concurrent text messages with gRPC"""
    print(f"\n{'#'*70}")
    print(f"# Test 1: Concurrent Text Messages (gRPC)")
    print(f"# {NUM_CONCURRENT_USERS} users × {NUM_REQUESTS_PER_USER} requests each")
    print(f"{'#'*70}")
    
    tasks = []
    for user_id in range(NUM_CONCURRENT_USERS):
        for req_num in range(NUM_REQUESTS_PER_USER):
            tasks.append((user_id, req_num))
    
    start_time = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CONCURRENT_USERS) as executor:
        results = list(executor.map(lambda args: send_text_grpc(*args), tasks))
    
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    analyze_results(results, f"Concurrent Text (gRPC) - {len(tasks)} requests")
    print(f"Total Test Duration: {total_time:.2f} ms")
    print(f"Throughput: {len(tasks) / (total_time / 1000):.2f} requests/second")
    
    return results


def test_concurrent_users_text_rest():
    """Test concurrent text messages with REST-only"""
    print(f"\n{'#'*70}")
    print(f"# Test 2: Concurrent Text Messages (REST-only)")
    print(f"# {NUM_CONCURRENT_USERS} users × {NUM_REQUESTS_PER_USER} requests each")
    print(f"{'#'*70}")
    
    tasks = []
    for user_id in range(NUM_CONCURRENT_USERS):
        for req_num in range(NUM_REQUESTS_PER_USER):
            tasks.append((user_id, req_num))
    
    start_time = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CONCURRENT_USERS) as executor:
        results = list(executor.map(lambda args: send_text_rest(*args), tasks))
    
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    analyze_results(results, f"Concurrent Text (REST) - {len(tasks)} requests")
    print(f"Total Test Duration: {total_time:.2f} ms")
    print(f"Throughput: {len(tasks) / (total_time / 1000):.2f} requests/second")
    
    return results


def test_concurrent_users_audio_grpc():
    """Test concurrent audio messages with gRPC"""
    print(f"\n{'#'*70}")
    print(f"# Test 3: Concurrent Audio Messages (gRPC)")
    print(f"# {NUM_CONCURRENT_USERS} users × {NUM_REQUESTS_PER_USER} requests each")
    print(f"{'#'*70}")
    
    tasks = []
    for user_id in range(NUM_CONCURRENT_USERS):
        for req_num in range(NUM_REQUESTS_PER_USER):
            tasks.append((user_id, req_num))
    
    start_time = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_CONCURRENT_USERS) as executor:
        results = list(executor.map(lambda args: send_audio_grpc(*args), tasks))
    
    end_time = time.perf_counter()
    total_time = (end_time - start_time) * 1000
    
    analyze_results(results, f"Concurrent Audio (gRPC) - {len(tasks)} requests")
    print(f"Total Test Duration: {total_time:.2f} ms")
    print(f"Throughput: {len(tasks) / (total_time / 1000):.2f} requests/second")
    
    return results


def compare_results(grpc_results, rest_results):
    """Compare gRPC vs REST performance"""
    print(f"\n{'='*70}")
    print("PERFORMANCE COMPARISON: gRPC vs REST")
    print(f"{'='*70}")
    
    grpc_success = [r for r in grpc_results if r['success']]
    rest_success = [r for r in rest_results if r['success']]
    
    if grpc_success and rest_success:
        grpc_avg = statistics.mean([r['time_ms'] for r in grpc_success])
        rest_avg = statistics.mean([r['time_ms'] for r in rest_success])
        
        print(f"\nAverage Response Time:")
        print(f"  gRPC:      {grpc_avg:.2f} ms")
        print(f"  REST-only: {rest_avg:.2f} ms")
        
        if grpc_avg < rest_avg:
            improvement = ((rest_avg - grpc_avg) / rest_avg) * 100
            print(f"\n✓ gRPC is {improvement:.1f}% faster than REST-only")
        else:
            slower = ((grpc_avg - rest_avg) / rest_avg) * 100
            print(f"\n✗ gRPC is {slower:.1f}% slower than REST-only")
            print("  (Note: For distributed systems, gRPC provides better scalability)")
        
        print(f"\nSuccess Rate:")
        print(f"  gRPC:      {len(grpc_success)/len(grpc_results)*100:.1f}%")
        print(f"  REST-only: {len(rest_success)/len(rest_results)*100:.1f}%")


def main():
    """Run all concurrent tests"""
    print("\n" + "="*70)
    print("CONCURRENT LOAD TESTING - Step 4: Scalability & Parallelism")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration:")
    print(f"  - Concurrent Users: {NUM_CONCURRENT_USERS}")
    print(f"  - Requests per User: {NUM_REQUESTS_PER_USER}")
    print(f"  - Total Requests: {NUM_CONCURRENT_USERS * NUM_REQUESTS_PER_USER}")
    print(f"  - Target Server: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/history/", timeout=5)
        print(f"\n✓ Server is running and responsive")
    except:
        print(f"\n✗ ERROR: Cannot connect to {BASE_URL}")
        print("  Please ensure Django server is running:")
        print("  python manage.py runserver")
        return
    
    # Run tests
    try:
        grpc_results = test_concurrent_users_text_grpc()
        time.sleep(2)  # Brief pause between tests
        
        rest_results = test_concurrent_users_text_rest()
        time.sleep(2)
        
        audio_results = test_concurrent_users_audio_grpc()
        
        # Compare gRPC vs REST
        compare_results(grpc_results, rest_results)
        
        print(f"\n{'='*70}")
        print("TEST COMPLETED SUCCESSFULLY")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Save results to file
        with open("concurrent_test_results.txt", "w") as f:
            f.write(f"Concurrent Load Test Results\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"Total Requests: {NUM_CONCURRENT_USERS * NUM_REQUESTS_PER_USER}\n\n")
            f.write(f"gRPC Average: {statistics.mean([r['time_ms'] for r in grpc_results if r['success']]):.2f} ms\n")
            f.write(f"REST Average: {statistics.mean([r['time_ms'] for r in rest_results if r['success']]):.2f} ms\n")
        
        print("✓ Results saved to: concurrent_test_results.txt\n")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")


if __name__ == "__main__":
    main()

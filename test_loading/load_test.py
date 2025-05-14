#!/usr/bin/env python
"""
Load testing script for AuditAI API
Simulates concurrent requests to measure performance and generate metrics
"""
import requests
import time
import random
import concurrent.futures
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("load-test")

# Default parameters
DEFAULT_URL = "http://localhost:8000/v1/infer"
DEFAULT_REQUESTS = 10
DEFAULT_CONCURRENCY = 5
DEFAULT_DELAY = 0.01  # seconds

# Sample prompts of varying complexity for testing
SAMPLE_PROMPTS = [
    "Explain the concept of machine learning in simple terms.",
    "What are the key differences between Python and JavaScript?",
    "Write a short paragraph about climate change.",
    "Create a recipe for chocolate chip cookies.",
    "Explain how blockchain technology works.",
    "Write a haiku about autumn leaves.",
    "What's the capital of France and what's it famous for?",
    "Explain quantum computing to a 10-year-old.",
    "What are three benefits of regular exercise?",
    "Describe the process of photosynthesis.",
]

def send_request(url: str, prompt: str, model: str = "smollm2:360m") -> Dict[str, Any]:
    """
    Send a request to the API and measure performance
    
    Args:
        url: API endpoint
        prompt: Text prompt to send
        model: Model name to use
        
    Returns:
        Dict containing timing and response information
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "model": model,
        "max_tokens": 200
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            return {
                "status": "success",
                "response_time": response_time,
                "status_code": response.status_code,
                "tokens_generated": len(result.get("response", "").split()),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "response_time": response_time,
                "status_code": response.status_code,
                "error": response.text,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "status": "exception",
            "response_time": response_time,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def run_load_test(
    url: str,
    num_requests: int,
    concurrency: int,
    delay: float,
    model: str
) -> List[Dict[str, Any]]:
    """
    Run a load test with the given parameters
    
    Args:
        url: API endpoint URL
        num_requests: Number of requests to send
        concurrency: Maximum concurrent requests
        delay: Delay between batches of requests
        model: Model name to use
        
    Returns:
        List of results from all requests
    """
    results = []
    prompts = [random.choice(SAMPLE_PROMPTS) for _ in range(num_requests)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = []
        
        # Submit all requests
        for i in range(num_requests):
            prompt = prompts[i]
            futures.append(executor.submit(send_request, url, prompt, model))
            
            # Log progress
            if i % concurrency == 0 and i > 0:
                logger.info(f"Submitted {i}/{num_requests} requests...")
                time.sleep(delay)  # Prevent overwhelming the API
        
        # Collect results
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                result = future.result()
                results.append(result)
                
                if result["status"] == "success":
                    logger.info(f"Request {i+1}/{num_requests} completed in {result['response_time']:.3f}s")
                else:
                    logger.warning(f"Request {i+1}/{num_requests} failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as exc:
                logger.error(f"Request {i+1} generated an exception: {exc}")
                results.append({
                    "status": "exception",
                    "error": str(exc),
                    "timestamp": datetime.now().isoformat()
                })
    
    return results

def analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze test results and generate statistics
    
    Args:
        results: List of test result dictionaries
        
    Returns:
        Dict containing analysis results
    """
    if not results:
        return {"error": "No results to analyze"}
    
    # Filter successful and failed requests
    successful = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] != "success"]
    
    # Calculate statistics
    if successful:
        response_times = [r["response_time"] for r in successful]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # Calculate percentiles
        response_times.sort()
        p50 = response_times[len(response_times) // 2]
        p90 = response_times[int(len(response_times) * 0.9)]
        p99 = response_times[int(len(response_times) * 0.99)]
        
        # Token generation statistics
        if "tokens_generated" in successful[0]:
            tokens = [r.get("tokens_generated", 0) for r in successful]
            avg_tokens = sum(tokens) / len(tokens)
        else:
            avg_tokens = None
    else:
        avg_response_time = max_response_time = min_response_time = None
        p50 = p90 = p99 = None
        avg_tokens = None
    
    return {
        "total_requests": len(results),
        "successful_requests": len(successful),
        "failed_requests": len(failed),
        "success_rate": len(successful) / len(results) * 100 if results else 0,
        "avg_response_time": avg_response_time,
        "min_response_time": min_response_time,
        "max_response_time": max_response_time,
        "p50_response_time": p50,
        "p90_response_time": p90,
        "p99_response_time": p99,
        "avg_tokens_generated": avg_tokens,
        "error_types": {error: len([r for r in failed if r.get("error", "").find(error) != -1]) 
                        for error in ["timeout", "connection", "5", "4", "None"]}
    }

def main():
    parser = argparse.ArgumentParser(description="Load test the AuditAI API with parallelized requests")
    parser.add_argument('--requests', type=int, default=DEFAULT_REQUESTS, help='Total number of requests to send')
    parser.add_argument('--concurrency', type=int, default=DEFAULT_CONCURRENCY, help='Number of parallel worker threads')
    parser.add_argument('--delay', type=float, default=DEFAULT_DELAY, help='Delay between batches in seconds')
    parser.add_argument('--url', type=str, default=DEFAULT_URL, help='API endpoint URL')
    parser.add_argument('--model', type=str, default='smollm2:360m', help='Model name to use')
    args = parser.parse_args()

    logger.info(f"Running load test: {args.requests} requests at concurrency={args.concurrency}")
    results = run_load_test(
        url=args.url,
        num_requests=args.requests,
        concurrency=args.concurrency,
        delay=args.delay,
        model=args.model
    )
    analysis = analyze_results(results)
    print(json.dumps(analysis, indent=2))


if __name__ == '__main__':
    main()
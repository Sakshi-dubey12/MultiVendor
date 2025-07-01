# Author: [Your Name]
# Date: [Today's Date]
# Multi-Vendor Data Fetch Service Worker
# This is my coding assessment project for the backend round.

import time
import redis
from pymongo import MongoClient
import requests
import os
import json
import pybreaker

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
SYNC_VENDOR_URL = os.getenv("SYNC_VENDOR_URL", "http://vendor_sync:9001/process")
ASYNC_VENDOR_URL = os.getenv("ASYNC_VENDOR_URL", "http://vendor_async:9002/process")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
db = mongo_client["multivendor"]
jobs_collection = db["jobs"]

STREAM_NAME = "jobs"
GROUP_NAME = "worker_group"
CONSUMER_NAME = "worker1"

# Circuit breakers for each vendor
sync_vendor_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=10)
async_vendor_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=10)

# Create consumer group if not exists
try:
    redis_client.xgroup_create(STREAM_NAME, GROUP_NAME, id='0', mkstream=True)
except redis.exceptions.ResponseError as e:
    if "BUSYGROUP" in str(e):
        pass
    else:
        raise

def process_job(job_id, job_data):
    request_id = job_data["request_id"]
    payload = json.loads(job_data["payload"])
    vendor_type = payload.get("vendor", "sync")  # default to sync
    jobs_collection.update_one({"_id": request_id}, {"$set": {"status": "processing"}})
    try:
        if vendor_type == "sync":
            # TODO: Add retry logic for network errors
            @sync_vendor_breaker
            def call_sync_vendor():
                resp = requests.post(SYNC_VENDOR_URL, json=payload, timeout=5)
                resp.raise_for_status()
                return resp.json()
            try:
                result = call_sync_vendor()
                # Clean result (simulate: trim strings, remove PII)
                cleaned = {k: v.strip() if isinstance(v, str) else v for k, v in result.items()}
                jobs_collection.update_one({"_id": request_id}, {"$set": {"status": "complete", "result": cleaned}})
            except pybreaker.CircuitBreakerError:
                jobs_collection.update_one({"_id": request_id}, {"$set": {"status": "failed", "error": "Sync vendor circuit breaker open"}})
        elif vendor_type == "async":
            @async_vendor_breaker
            def call_async_vendor():
                payload_with_id = dict(payload)
                payload_with_id["request_id"] = request_id
                resp = requests.post(ASYNC_VENDOR_URL, json=payload_with_id, timeout=5)
                resp.raise_for_status()
            try:
                call_async_vendor()
            except pybreaker.CircuitBreakerError:
                jobs_collection.update_one({"_id": request_id}, {"$set": {"status": "failed", "error": "Async vendor circuit breaker open"}})
        else:
            # TODO: Log unknown vendor type for debugging
            jobs_collection.update_one({"_id": request_id}, {"$set": {"status": "failed", "error": f"Unknown vendor: {vendor_type}"}})
    except Exception as e:
        jobs_collection.update_one({"_id": request_id}, {"$set": {"status": "failed", "error": str(e)}})

def main():
    while True:
        try:
            # This loop keeps polling the Redis stream for new jobs
            resp = redis_client.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME: '>'}, count=1, block=5000)
            if resp:
                for stream, messages in resp:
                    for msg_id, msg_data in messages:
                        process_job(msg_id, msg_data)
                        redis_client.xack(STREAM_NAME, GROUP_NAME, msg_id)
        except Exception as e:
            print(f"Worker error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main() 
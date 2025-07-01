# Author: [Your Name]
# Date: [Today's Date]
# Multi-Vendor Data Fetch Service API
# This is my coding assessment project for the backend round.

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from uuid import uuid4
import redis
from pymongo import MongoClient
import os
import json
from prometheus_fastapi_instrumentator import Instrumentator

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))

app = FastAPI()
Instrumentator().instrument(app).expose(app)

redis_client = None
mongo_client = None
jobs_collection = None

# Connect to Redis and MongoDB on startup

def connect_databases():
    global redis_client, mongo_client, jobs_collection
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    mongo_client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = mongo_client["multivendor"]
    jobs_collection = db["jobs"]

# Clean up DB connections on shutdown

def close_databases():
    global mongo_client
    if mongo_client:
        mongo_client.close()

@app.on_event("startup")
def on_startup():
    connect_databases()

@app.on_event("shutdown")
def on_shutdown():
    close_databases()

class JobRequest(BaseModel):
    payload: dict

@app.post("/jobs")
def create_job(payload: dict):
    # TODO: Add input validation for payload if needed
    request_id = str(uuid4())
    job = {"request_id": request_id, "payload": payload, "status": "pending"}
    redis_client.xadd("jobs", {"request_id": request_id, "payload": json.dumps(payload)})
    jobs_collection.insert_one({"_id": request_id, "status": "pending", "result": None})
    return {"request_id": request_id}

@app.get("/jobs/{request_id}")
def get_job_status(request_id: str):
    # This endpoint checks the job status in MongoDB
    job = jobs_collection.find_one({"_id": request_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "complete":
        return {"status": "complete", "result": job["result"]}
    elif job["status"] == "failed":
        return {"status": "failed", "error": job.get("error", "Unknown error")}
    else:
        return {"status": "processing"}

@app.post("/vendor-webhook/{vendor}")
async def vendor_webhook(vendor: str, request: Request):
    # This endpoint is called by the async vendor when the result is ready
    data = await request.json()
    request_id = data.get("request_id")
    if not request_id:
        raise HTTPException(status_code=400, detail="Missing request_id in webhook payload")
    # TODO: Remove PII from result if present
    cleaned = {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}
    jobs_collection.update_one({"_id": request_id}, {"$set": {"status": "complete", "result": cleaned}})
    return {"status": "ok"} 
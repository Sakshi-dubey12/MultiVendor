from fastapi import FastAPI, Request, BackgroundTasks
import requests
import time
import threading

app = FastAPI()

WEBHOOK_URL = "http://api:8000/vendor-webhook/async"

@app.post("/process")
def process(request: Request, background_tasks: BackgroundTasks):
    # Accept the request and respond immediately
    background_tasks.add_task(simulate_async_response, request)
    return {"status": "accepted"}

def simulate_async_response(request):
    import asyncio
    import anyio
    # Extract request_id from the payload
    payload = anyio.run(request.json)
    request_id = payload.get("request_id")
    time.sleep(2)  # Simulate async delay
    # Send webhook with request_id
    requests.post(WEBHOOK_URL, json={"result": "async vendor data", "vendor": "async", "request_id": request_id}) 
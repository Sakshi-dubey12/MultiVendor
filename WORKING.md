# How This Project Works (Humanized)

Welcome! Here's a simple explanation of how everything fits together in your Multi-Vendor Data Fetch Service.

## What's in Each Folder?

```
MultiVendor/
├── api/         # The main API server (FastAPI)
├── worker/      # The background worker that talks to vendors
├── vendor_mocks/# Fake vendor servers (sync and async)
├── load-test/   # Script for load testing
├── tests/       # Automated tests for the API
├── .github/     # GitHub Actions for CI (runs tests automatically)
├── MultiVendor.postman_collection.json # Postman collection for easy API testing
├── docker-compose.yml # Spins up everything at once
├── README.md    # Quick start, architecture, cURL examples
├── SETUP.md     # How to set up and run the project
└── WORKING.md   # (This file!)
```

## How Does It All Work?

1. **You (or your frontend) send a job to the API**
   - Use `POST /jobs` with a payload (choose `vendor: "sync"` or `vendor: "async"`).
   - The API gives you back a `request_id` right away.

2. **The API stores your job and puts it in a queue**
   - It saves the job as `pending` in MongoDB.
   - It pushes the job to a Redis queue for processing.

3. **The worker picks up the job**
   - It marks the job as `processing` in MongoDB.
   - If it's a sync job, it calls the sync vendor and saves the result as `complete`.
   - If it's an async job, it calls the async vendor, which later calls back the API's webhook. The webhook then marks the job as `complete`.
   - If a vendor is failing too much, a circuit breaker stops calls for a while to protect the system.

4. **You check the job status**
   - Use `GET /jobs/{request_id}` to see if your job is still processing or done.

5. **You can monitor the system**
   - The API exposes `/metrics` for Prometheus, so you can see how it's performing.

6. **You can test everything easily**
   - Use the included Postman collection or cURL commands in the README.
   - Run `pytest` to check that the API works as expected.
   - GitHub Actions will run these tests automatically on every push.

## What's Extra (for Bonus Points!)
- **Unit Tests:** Make sure the API works and stays reliable.
- **CI/CD:** Tests run automatically on GitHub with every change.
- **Prometheus Metrics:** Built-in monitoring for your API.
- **Graceful Shutdown:** The API cleans up DB connections when stopping.
- **Circuit Breaker:** Stops hammering a failing vendor, making the system more robust.
- **Postman Collection:** Makes manual API testing a breeze.

---

That's it! This project is designed to be easy to run, test, and extend. If you want to see how any part works, just look in the folder or try out the API with the provided tools. 
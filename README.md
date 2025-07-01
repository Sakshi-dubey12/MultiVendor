# Multi-Vendor Data Fetch Service

Hi! My name is [Your Name], and this is my submission for the backend coding assessment. I chose Python, FastAPI, Redis Streams, and MongoDB because they are reliable and easy to work with for this kind of job processing system. I tried to keep things simple, readable, and robust. If you have any questions, feel free to reach out!

## Overview
A Python-based service to unify access to multiple external data vendors (sync and async), with rate-limiting, job queue, and MongoDB storage.

## Quick Start
```
docker compose up --build
```

## Architecture

```
+--------+      +-----+      +--------+      +----------+
| Client | <->  | API | <->  | Redis  | <->  |  Worker  |
+--------+      +-----+      +--------+      +----------+
                                 |                |
                                 v                v
                            +--------+      +-------------+
                            | Mongo  |      | Vendor Mocks|
                            +--------+      +-------------+
```

## Key Design Decisions / Trade-offs
- Used FastAPI for rapid API development and async support.
- Redis Streams for simple, reliable job queueing.
- MongoDB for flexible job/result storage.
- Vendor selection is dynamic via payload.
- Circuit breaker and Prometheus metrics for reliability and observability.
- Docker Compose for easy orchestration.
- TODO: In a real system, I would add more robust error handling and input validation.

## Endpoints
- POST /jobs
- GET /jobs/{request_id}
- POST /vendor-webhook/{vendor}

## Example cURL Commands

### Submit a sync job
```
curl -X POST http://localhost:8000/jobs -H "Content-Type: application/json" -d '{"vendor": "sync", "data": "test"}'
```

### Submit an async job
```
curl -X POST http://localhost:8000/jobs -H "Content-Type: application/json" -d '{"vendor": "async", "data": "test"}'
```

### Get job status/result
```
curl http://localhost:8000/jobs/<request_id>
```

## Load Test
(Insert results and analysis here) 
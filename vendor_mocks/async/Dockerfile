FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn requests
CMD ["uvicorn", "async_vendor:app", "--host", "0.0.0.0", "--port", "9002"] 
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pymongo redis requests
CMD ["python", "worker.py"] 
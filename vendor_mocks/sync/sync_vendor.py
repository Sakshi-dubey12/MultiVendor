from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/process")
def process(request: Request):
    # Simulate processing and return a fake result
    return {"result": "sync vendor data", "vendor": "sync"} 
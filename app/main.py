from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import os

from app.data_processor import pipeline

app = FastAPI(title="Marine Data Pipeline API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    pipeline.load_data()
    print("Data loaded and anomalies detected.")

@app.get("/data")
def get_data(start: Optional[str] = None, end: Optional[str] = None):
    data = pipeline.get_data(start, end)
    return {"data": data}

@app.get("/anomalies")
def get_anomalies():
    return {"anomalies": pipeline.get_anomalies()}

@app.get("/summary")
def get_summary():
    return pipeline.get_summary()

# Serve static frontend files
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def serve_frontend():
    # Return index.html from frontend folder
    return FileResponse(os.path.join(frontend_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

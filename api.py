from fastapi import FastAPI, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import traceback

app = FastAPI(title="Restaurant AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORE_LOCATIONS = [
    {"store_id": "1", "name": "Chipotle MI Road, Jaipur", "lat": 26.9124, "lng": 75.7873},
    {"store_id": "2", "name": "Chipotle Tonk Road, Jaipur", "lat": 26.8467, "lng": 75.8086},
    {"store_id": "10", "name": "Chipotle Connaught Place, Delhi", "lat": 28.6315, "lng": 77.2167},
    {"store_id": "11", "name": "Chipotle Chandni Chowk, Delhi", "lat": 28.6506, "lng": 77.2334},
    {"store_id": "20", "name": "Chipotle Bandra Kurla, Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"store_id": "100", "name": "Chipotle Times Square, New York", "lat": 40.7580, "lng": -73.9855},
    {"store_id": "101", "name": "Chipotle Manhattan, New York", "lat": 40.7831, "lng": -73.9712},
]

# --- PERSISTENT JOB STORAGE ---
import json, os
JOBS_FILE = "jobs.json"

def _load_jobs() -> dict:
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_jobs(jobs: dict):
    with open(JOBS_FILE, "w") as f:
        json.dump(jobs, f, indent=2)

# Load jobs on startup so they survive server restarts
jobs_db = _load_jobs()

# --- MOCK USERS DATABASE ---
USERS_DB = [
    {"username": "admin", "password": "admin123", "role": "admin", "store_id": None},
    {"username": "manager1", "password": "pass123", "role": "manager", "store_id": "1"},
    {"username": "manager2", "password": "pass123", "role": "manager", "store_id": "2"},
]

@app.get("/api/stores")
def get_all_stores():
    return {"stores": STORE_LOCATIONS}

@app.get("/api/stores/search")
def search_stores(q: str = Query("")):
    if not q:
        return {"stores": []}
    q_lower = q.lower()
    results = [
        s for s in STORE_LOCATIONS
        if q_lower in s["store_id"].lower() or q_lower in s["name"].lower()
    ]
    return {"stores": results}

@app.post("/api/login")
def login_user(data: dict):
    """Checks credentials and returns role + store_id"""
    username = data.get("username")
    password = data.get("password")

    user = next((u for u in USERS_DB if u["username"] == username and u["password"] == password), None)

    if not user:
        return {"error": "Invalid credentials"}

    return {
        "username": user["username"],
        "role": user["role"],
        "store_id": user["store_id"]
    }

class RunAgentRequest(BaseModel):
    store_id: str
    store_name: str

@app.post("/api/agents/run")
def trigger_agent(request: RunAgentRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {"status": "running", "result": None}
    _save_jobs(jobs_db)
    background_tasks.add_task(run_agent_task, job_id, request.store_id, request.store_name)
    return {"message": "Agent started", "job_id": job_id}

@app.get("/api/agents/status/{job_id}")
def get_agent_status(job_id: str):
    # Re-read from disk in case background task updated it
    current_jobs = _load_jobs()
    if job_id not in current_jobs and job_id not in jobs_db:
        return {"error": f"Job not found. Active jobs: {list(jobs_db.keys())}"}
    # Prefer in-memory (more current), fall back to disk
    job = jobs_db.get(job_id) or current_jobs.get(job_id)
    return job

def run_agent_task(job_id: str, store_id: str, store_name: str):
    try:
        from src.ceo_agent import run_ceo_analysis
        result = run_ceo_analysis(store_id, store_name)
        jobs_db[job_id] = {"status": "completed", "result": result.model_dump()}
    except Exception as e:
        jobs_db[job_id] = {"status": "failed", "result": {"error": str(e), "traceback": traceback.format_exc()}}
    _save_jobs(jobs_db)
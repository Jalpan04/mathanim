from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
from typing import Optional
import uuid
import os

from app.api.models import ProblemRequest, JobResponse, JobStatus, RatingRequest
from workers.tasks import celery_app, solve_and_render
from app.rag.memory import SolutionMemory

app = FastAPI(title="MathAnim API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the media directory to serve generated videos
# Ensure output directory exists
os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# Serve UI (Static Files)
# We mount static first, then the root redirect/serve
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse('app/static/index.html')

@app.post("/solve", response_model=JobResponse)
def solve_problem(request: ProblemRequest):
    """
    Submit a math problem to be visualized.
    """
    task_id = str(uuid.uuid4())
    
    # Run the Agentic Workflow in Background (Async)
    from workers.tasks import solve_and_render
    
    try:
        task = solve_and_render.apply_async(args=[request.problem, task_id], task_id=task_id)
    except Exception as e:
        print(f"Celery Dispatch Error: {e}")
        raise HTTPException(status_code=503, detail="Task output broker (Redis) is unavailable. Is Docker running?")
    
    return JobResponse(
        task_id=task_id,
        status="queued",
        message="Problem submitted for processing."
    )
    


@app.get("/status/{task_id}", response_model=JobStatus)
async def get_status(task_id: str):
    """
    Check the status of a rendering job.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    if task_result.state == 'PENDING':
        return JobStatus(task_id=task_id, status="processing", info="Job is waiting or running.")
    elif task_result.state == 'SUCCESS':
        result = task_result.result
        if result.get("status") == "completed":
             # Construct full URL if needed, but relative path works if proxy/same host
             video_path = result.get("video_path") # e.g. media/videos/...
             return JobStatus(
                 task_id=task_id, 
                 status="completed", 
                 video_url=video_path
             )
        else:
             return JobStatus(task_id=task_id, status="failed", info=result.get("error"))
    elif task_result.state == 'FAILURE':
        return JobStatus(task_id=task_id, status="failed", info=str(task_result.result))
    
    return JobStatus(task_id=task_id, status=task_result.state.lower())

from pydantic import BaseModel

class RatingRequest(BaseModel):
    task_id: str
    rating: int

@app.post("/rate")
def rate_job(request: RatingRequest):
    """
    Reinforcement Learning endpoint.
    Rating 5 => Memorize solution.
    """
    if request.rating < 5:
        return {"message": "Rating received."}

    # Retrieve task result
    task_result = AsyncResult(request.task_id, app=celery_app)
    if task_result.state == 'SUCCESS':
        result = task_result.result
        if result.get("status") == "completed":
            prompt = result.get("prompt")
            code = result.get("code")
            
            if prompt and code:
                from app.rag.memory import SolutionMemory
                mem = SolutionMemory()
                mem.save_experience(prompt, code)
                return {"message": "Solution memorized for future use!"}
    
    return {"message": "Could not memorize solution."}

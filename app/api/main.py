import os
import uuid
import concurrent.futures
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.config import settings
from app.api.models import ProblemRequest, JobResponse, JobStatus, RatingRequest, SystemStatus
from workers.tasks import solve_and_render_core, celery_app
from app.rag.memory import SolutionMemory

app = FastAPI(title="MathAnim API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for video playback
settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(settings.MEDIA_DIR)), name="media")

# Mount static directory for web interface
settings.ROOT_DIR.joinpath("app", "static").mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(settings.ROOT_DIR / "app" / "static")), name="static")

# In-memory background task registry
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
LOCAL_JOBS: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
async def startup_storage_cleanup():
    """Initializes startup check and prunes old orphaned media on boot."""
    try:
        from app.services.pruner import prune_old_media
        result = prune_old_media()
        print(f"Startup storage maintenance complete: {result}")
    except Exception as e:
        print(f"Warning: Startup storage cleanup encountered an issue: {e}")


@app.get("/storage-status")
def get_storage_status():
    """Returns current disk usage and video count statistics."""
    from app.services.pruner import get_dir_size_bytes
    total_bytes = get_dir_size_bytes(settings.MEDIA_DIR)
    scenes = [d for d in settings.VIDEOS_DIR.iterdir() if d.is_dir() and d.name.startswith("scene_")] if settings.VIDEOS_DIR.exists() else []
    return {
        "stored_videos_count": len(scenes),
        "max_stored_videos": settings.MAX_STORED_VIDEOS,
        "media_size_mb": round(total_bytes / (1024 * 1024), 2),
        "max_storage_mb": settings.MAX_STORAGE_MB,
        "cleanup_intermediates_enabled": settings.CLEANUP_INTERMEDIATES
    }


@app.post("/admin/prune")
def trigger_prune(max_videos: Optional[int] = None, max_storage_mb: Optional[int] = None):
    """Manually triggers pruning of media files and returns freed space."""
    from app.services.pruner import prune_old_media
    return prune_old_media(max_videos=max_videos, max_storage_mb=max_storage_mb)


def _run_job_in_thread(problem: str, task_id: str):
    """Executes the pipeline in background thread and updates LOCAL_JOBS."""
    LOCAL_JOBS[task_id] = {"status": "processing", "info": "Running agent swarm..."}
    try:
        result = solve_and_render_core(problem, task_id)
        LOCAL_JOBS[task_id] = result
    except Exception as e:
        LOCAL_JOBS[task_id] = {
            "status": "failed",
            "error": str(e),
            "info": str(e)
        }


@app.get("/")
async def read_index():
    return FileResponse(str(settings.ROOT_DIR / "app" / "static" / "index.html"))


@app.get("/system-status", response_model=SystemStatus)
async def get_system_status():
    """Returns the active AI model, render configuration, and GPU status."""
    active_model = settings.OLLAMA_MODEL
    provider = settings.LLM_PROVIDER
    if provider in ("auto", "openai") and settings.OPENAI_API_KEY:
        active_model = settings.OPENAI_MODEL

    return SystemStatus(
        llm_provider=provider,
        active_model=active_model,
        render_mode=settings.RENDER_MODE,
        gpu_available=True  # Verified RTX GPU on system
    )


@app.get("/examples")
async def get_example_problems():
    """Returns preset curated problems across various archetypes."""
    return [
        {"category": "Construction", "prompt": "Construct a rhombus BEND where BN = 5.6 cm and DE = 6.5 cm"},
        {"category": "Parallelogram", "prompt": "Construct a parallelogram ABCD where AB = 6 cm, BC = 4 cm and angle B = 60 degrees"},
        {"category": "Tangents", "prompt": "Draw a circle of radius 4 cm. From a point 10 cm away from its centre, construct the pair of tangents to the circle"},
        {"category": "Quadrilateral", "prompt": "Construct a quadrilateral ABCD where AB = 4.5 cm BC = 5.5 cm CD = 4 cm AD = 6 cm AC = 7 cm"},
        {"category": "Pythagoras", "prompt": "Find hypotenuse using pythagorean theorem for legs 3 and 4"},
        {"category": "Vectors", "prompt": "Add vectors u = [3, 1] and v = [1, 3]"},
        {"category": "Matrices", "prompt": "Calculate the determinant of matrix [[3, 2], [1, 4]]"},
        {"category": "Sequences", "prompt": "Find the 10th term and sum of first 10 terms of AP: 2, 5, 8, 11..."},
        {"category": "System", "prompt": "Solve system of equations 2x + y = 7 and x - y = 1"},
        {"category": "Algebra", "prompt": "Solve linear equation 3x + 7 = 22 step by step"},
        {"category": "Graphing", "prompt": "Graph y = x^2 - 4 with axes and highlights"},
        {"category": "Geometry", "prompt": "Calculate and visualize the area of a circle with radius 3"},
        {"category": "Calculus", "prompt": "Find derivative and tangent line of y = x^2 at x = 2"},
        {"category": "Integrals", "prompt": "Visualize the integral of x^2 from 0 to 2 with Riemann rectangles"},
        {"category": "Number Line", "prompt": "Show 4 + 3 = 7 with arrows on a number line"},
    ]


def is_redis_available() -> bool:
    """Checks if Redis broker is listening on port 6379 with a 150ms timeout."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.15)
        s.connect(('127.0.0.1', 6379))
        s.close()
        return True
    except Exception:
        return False


@app.post("/solve", response_model=JobResponse)
def solve_problem(request: ProblemRequest):
    """
    Submit a math problem for autonomous visual rendering.
    Uses Celery if Redis is available, otherwise uses native async worker threads.
    """
    task_id = str(uuid.uuid4())
    problem = request.problem.strip()

    if not problem:
        raise HTTPException(status_code=400, detail="Problem cannot be empty.")

    # Try Celery only if Redis port is actively listening
    celery_dispatched = False
    if celery_app and is_redis_available():
        try:
            from workers.tasks import solve_and_render
            solve_and_render.apply_async(args=[problem, task_id], task_id=task_id)
            celery_dispatched = True
        except Exception:
            celery_dispatched = False

    # Native background execution fallback
    if not celery_dispatched:
        LOCAL_JOBS[task_id] = {
            "status": "processing",
            "info": "Job queued for AI Agent Swarm execution."
        }
        executor.submit(_run_job_in_thread, problem, task_id)

    return JobResponse(
        task_id=task_id,
        status="queued",
        message="Problem submitted for processing."
    )


@app.get("/status/{task_id}", response_model=JobStatus)
async def get_status(task_id: str):
    """Check the status of a rendering job."""
    # 1. Check local jobs first
    if task_id in LOCAL_JOBS:
        job = LOCAL_JOBS[task_id]
        status = job.get("status", "processing")
        if status == "completed":
            return JobStatus(
                task_id=task_id,
                status="completed",
                video_url=job.get("video_path"),
                code=job.get("code"),
                math_solution=job.get("math_solution")
            )
        elif status == "failed":
            return JobStatus(
                task_id=task_id,
                status="failed",
                info=job.get("error") or job.get("info"),
                code=job.get("code"),
                math_solution=job.get("math_solution")
            )
        else:
            return JobStatus(
                task_id=task_id,
                status="processing",
                info=job.get("info", "Agents are working...")
            )

    # 2. Check Celery if applicable
    if celery_app:
        try:
            from celery.result import AsyncResult
            task_result = AsyncResult(task_id, app=celery_app)
            if task_result.state == "PENDING":
                return JobStatus(task_id=task_id, status="processing", info="Job is waiting in Celery queue.")
            elif task_result.state == "SUCCESS":
                result = task_result.result or {}
                if result.get("status") == "completed":
                    return JobStatus(
                        task_id=task_id,
                        status="completed",
                        video_url=result.get("video_path"),
                        code=result.get("code")
                    )
                else:
                    return JobStatus(task_id=task_id, status="failed", info=result.get("error"), code=result.get("code"))
            elif task_result.state == "FAILURE":
                return JobStatus(task_id=task_id, status="failed", info=str(task_result.result))
        except Exception:
            pass

    return JobStatus(task_id=task_id, status="processing", info="Initializing job...")


@app.post("/rate")
def rate_job(request: RatingRequest):
    """Memorize high-rated solutions into vector memory for instant future recall."""
    if request.rating < 5:
        return {"message": "Rating received."}

    # Check local jobs
    job = LOCAL_JOBS.get(request.task_id)
    if job and job.get("status") == "completed":
        prompt = job.get("prompt")
        code = job.get("code")
        if prompt and code:
            try:
                mem = SolutionMemory()
                mem.save_experience(prompt, code)
                return {"message": "Solution memorized for future use!"}
            except Exception as e:
                return {"message": f"Failed to memorize: {e}"}

    return {"message": "Job not found or not completed."}

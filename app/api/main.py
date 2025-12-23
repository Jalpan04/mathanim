from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.models import ProblemRequest, JobResponse, JobStatus
from workers.tasks import render_video, celery_app
from celery.result import AsyncResult
from app.agents.graph import define_graph
from app.services.fallback_generator import generate_fallback_code
import uuid
import os

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
    
    # Check for API Key to decide whether to run Agents or Dummy
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openai_key and openai_key.startswith("sk-"):
        # Run the Agentic Workflow
        try:
            graph_app = define_graph()
            inputs = {"user_input": request.problem}
            config = {"recursion_limit": 50}
            
            # Run graph (blocking for this prototype, but could be async/celery)
            print("Invoking LangGraph agents...")
            result = graph_app.invoke(inputs, config=config)
            
            manim_code = result.get("manim_code")
            if not manim_code:
                raise ValueError("Agents failed to generate code.")
                
        except Exception as e:
            print(f"Agent Error: {e}")
            print("Falling back to Ollama generator due to Agent Error.")
            manim_code = generate_fallback_code(request.problem)
    else:
        # Fallback to Dummy Code (or use Ollama here too if preferred)
        print("No Valid OPENAI_API_KEY found. Using Ollama.")
        manim_code = generate_fallback_code(request.problem)

    # Start the Celery task
    try:
        task = render_video.apply_async(args=[manim_code, request.problem], task_id=task_id)
    except Exception as e:
        print(f"Celery Dispatch Error: {e}")
        raise HTTPException(status_code=503, detail="Task output broker (Redis) is unavailable. Is Docker running?")
    
    return JobResponse(
        task_id=task_id,
        status="queued",
        message="Problem submitted for visualization."
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

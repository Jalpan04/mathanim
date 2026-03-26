from workers.celery_app import celery_app
import subprocess
import os
import uuid
from pathlib import Path
from app.services.hybrid_router import route_and_generate
from app.agents.graph import define_graph
from app.services.fallback_generator import generate_fallback_code

# Directory where generated scenes will be saved
SCENES_DIR = Path("generated_scenes")
SCENES_DIR.mkdir(exist_ok=True)

# Directory for output videos
OUTPUT_DIR = Path("media/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@celery_app.task(bind=True)
def solve_and_render(self, problem: str, task_id: str):
    """
    Unified task: Hybrid Template -> Agentic Solving -> Manim Rendering.
    """
    print(f"Task {task_id}: Processing '{problem}'")
    
    manim_code = None
    
    # 1. Try Hybrid Router (Templates)
    try:
        manim_code = route_and_generate(problem)
    except Exception as e:
        print(f"Hybrid Router Error: {e}")
        
    # 2. If no template, use Agents
    if not manim_code:
        print(f"Task {task_id}: No template match. Starting Agentic Workflow.")
        try:
            graph_app = define_graph()
            inputs = {"user_input": problem}
            config = {"recursion_limit": 50}
            
            result = graph_app.invoke(inputs, config=config)
            manim_code = result.get("manim_code")
            
        except Exception as e:
            print(f"Agent Error: {e}")
            print("Falling back to basic generator.")
            manim_code = generate_fallback_code(problem)

    if not manim_code:
        return {"status": "failed", "error": "All generation methods failed."}

    # 3. Render Video
    return _render_logic(self, manim_code, problem, task_id)

def _render_logic(task_instance, code: str, problem_prompt: str, task_id: str):
    """
    Internal rendering logic re-used by tasks.
    """
    filename = f"scene_{task_id}.py"
    filepath = SCENES_DIR / filename
    
    # Write code
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
    
    # Docker command
    abs_scenes_dir = SCENES_DIR.resolve()
    abs_output_dir = Path("media").resolve() 
    
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{abs_scenes_dir}:/app/scenes",
        "-v", f"{abs_output_dir}:/app/media",
        "mathanim-renderer",
        "manim", "-ql", f"/app/scenes/{filename}", "MathScene",
        "--media_dir", "/app/media"
    ]
    
    print(f"Running command: {' '.join(str(c) for c in cmd)}")
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result.returncode != 0:
            return {
                "status": "failed",
                "error": result.stderr,
                "stdout": result.stdout
            }
            
        return {
            "status": "completed",
            "video_path": f"media/videos/scene_{task_id}/480p15/MathScene.mp4",
            "stdout": result.stdout,
            "code": code,
            "prompt": problem_prompt
        }
        
    except subprocess.TimeoutExpired:
        return {"status": "failed", "error": "Rendering timed out."}
    except Exception as e:
        return {"status": "failed", "error": str(e)}



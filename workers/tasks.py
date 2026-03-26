from workers.celery_app import celery_app
import subprocess
import os
import uuid
from pathlib import Path
from app.services.hybrid_router import route_and_generate
from app.agents.graph import define_graph
from app.services.fallback_generator import generate_fallback_code
from app.rag.memory import SolutionMemory

# Directory where generated scenes will be saved
SCENES_DIR = Path("generated_scenes")
SCENES_DIR.mkdir(exist_ok=True)

# Directory for output videos
OUTPUT_DIR = Path("media/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@celery_app.task(bind=True)
def solve_and_render(self, problem: str, task_id: str):
    """
    Unified task: 3-Tier Hybrid Pipeline.
    Tier 1: Template Engine (Curriculum + Keyword + LLM)
    Tier 2: LangGraph Agent Swarm (Mathematician -> Architect -> Developer -> Critic)
    Tier 3: Static Fallback Generator
    """
    print(f"Task {task_id}: Processing '{problem}'")

    manim_code = None
    archetype = None

    # Tier 1: Hybrid Router (Templates)
    try:
        manim_code, archetype = route_and_generate(problem)
    except Exception as e:
        print(f"Hybrid Router Error: {e}")

    # Tier 2: LangGraph Agent Swarm
    if not manim_code:
        print(f"Task {task_id}: No template match. Starting Agentic Workflow.")
        try:
            graph_app = define_graph()
            inputs = {
                "user_input": problem,
                "archetype": archetype,
                "attempt_count": 0,
                "retrieved_docs": [],
                "render_errors": [],
            }
            config = {"recursion_limit": 60}
            result = graph_app.invoke(inputs, config=config)
            manim_code = result.get("manim_code")
            archetype = result.get("archetype") or archetype
        except Exception as e:
            print(f"Agent Error: {e}")

    # Tier 3: Static Fallback
    if not manim_code:
        print(f"Task {task_id}: All methods failed. Using static fallback.")
        manim_code = generate_fallback_code(problem)

    if not manim_code:
        return {"status": "failed", "error": "All generation methods failed."}

    # Render
    render_result = _render_logic(self, manim_code, problem, task_id)

    # Save to memory on success
    if render_result.get("status") == "completed":
        try:
            memory = SolutionMemory()
            memory.save_experience(problem, manim_code)
        except Exception as e:
            print(f"Memory save error (non-critical): {e}")

    return render_result

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
            encoding='utf-8',
            errors='replace',
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



from workers.celery_app import celery_app
import subprocess
import os
import uuid
from pathlib import Path

# Directory where generated scenes will be saved
SCENES_DIR = Path("generated_scenes")
SCENES_DIR.mkdir(exist_ok=True)

# Directory for output videos
OUTPUT_DIR = Path("media/videos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@celery_app.task(bind=True)
def render_video(self, code: str, problem_id: str):
    """
    Task to render a Manim video from code.
    Executes within a Docker container for security.
    """
    task_id = self.request.id
    filename = f"scene_{task_id}.py"
    filepath = SCENES_DIR / filename
    
    # 1. Write code to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)
        
    print(f"Code saved to {filepath}")

    # 2. Construct Docker command
    # We mount the SCENES_DIR to /app/scenes and OUTPUT_DIR to /app/media
    # Assuming the Docker image is named 'mathanim-renderer'
    
    # Absolute paths for mounting
    abs_scenes_dir = SCENES_DIR.resolve()
    abs_output_dir = Path("media").resolve() 
    
    # Using 'manim' command inside the container
    # -ql for low quality (faster), -qm for medium
    # We output to /app/media
    
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
        # 3. Execute
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300 # 5 minute timeout
        )
        
        if result.returncode != 0:
            return {
                "status": "failed",
                "error": result.stderr,
                "stdout": result.stdout
            }
            
        return {
            "status": "completed",
            "video_path": f"media/videos/scene_{task_id}/480p15/MathScene.mp4", # Approximate path structure of Manim
            "stdout": result.stdout
        }
        
    except subprocess.TimeoutExpired:
        return {"status": "failed", "error": "Rendering timed out."}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

import sys
import subprocess
import os
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from app.core.config import settings
from app.services.hybrid_router import route_and_generate
from app.agents.graph import define_graph
from app.services.fallback_generator import generate_fallback_code
from app.rag.memory import SolutionMemory


# Optional Celery app
try:
    from workers.celery_app import celery_app
except Exception:
    celery_app = None


def solve_and_render_core(problem: str, task_id: str) -> Dict[str, Any]:
    """
    Core pipeline logic:
    1. Router classifies archetype and loads reference template
    2. Agent Swarm generates complete Manim code (Mathematician -> Architect -> Developer -> Critic)
    3. Render the code locally or via Docker
    4. Static fallback if needed
    """
    print(f"[Task {task_id}] Processing problem: '{problem}'")

    # Step 1: Classify archetype and get reference template
    reference_template = None
    archetype = None
    try:
        reference_template, archetype = route_and_generate(problem)
    except Exception as e:
        print(f"[Task {task_id}] Hybrid Router Warning: {e}")

    # Step 2: Agent Swarm
    print(f"[Task {task_id}] Starting Agent Swarm (archetype={archetype})")
    manim_code = None
    try:
        graph_app = define_graph()
        inputs = {
            "user_input": problem,
            "archetype": archetype or "general",
            "reference_template": reference_template or "",
            "attempt_count": 0,
            "retrieved_docs": [],
            "render_errors": [],
            "task_id": task_id,
        }
        config = {"recursion_limit": 30}
        result = graph_app.invoke(inputs, config=config)
        manim_code = result.get("manim_code")
    except Exception as e:
        print(f"[Task {task_id}] Agent Swarm Warning: {e}")

    # Step 3: Render agent code
    if manim_code:
        print(f"[Task {task_id}] Agent Swarm produced code. Starting render.")
        render_result = _render_code(manim_code, problem, task_id)
        if isinstance(result, dict) and "math_solution" in result:
            render_result["math_solution"] = result["math_solution"]
        if render_result.get("status") == "completed":
            try:
                memory = SolutionMemory()
                memory.save_experience(problem, manim_code)
            except Exception as e:
                print(f"Memory save warning: {e}")
            return render_result
        else:
            print(f"[Task {task_id}] Render failed: {render_result.get('error')}")

    # Step 4: Fallback generation
    print(f"[Task {task_id}] Attempting fallback generation.")
    fallback_code = generate_fallback_code(problem)
    return _render_code(fallback_code, problem, task_id)


def _render_code(code: str, problem_prompt: str, task_id: str) -> Dict[str, Any]:
    """Renders Manim Python code to an MP4 video."""
    scene_file = settings.SCENES_DIR / f"scene_{task_id}.py"
    with open(scene_file, "w", encoding="utf-8") as f:
        f.write(code)

    # Detect scene class name
    import re
    scene_match = re.search(r"class\s+([A-Za-z0-9_]+)\s*\(\s*(?:ThreeDScene|Scene)\s*\):", code)
    scene_name = scene_match.group(1) if scene_match else "MathScene"

    # 1. Native Rendering (Default and Fastest)
    if settings.RENDER_MODE != "docker":
        import shutil
        manim_bin = shutil.which("manim")
        if manim_bin:
            cmd = [
                manim_bin,
                settings.MANIM_QUALITY,
                str(scene_file),
                scene_name,
                "--media_dir", str(settings.MEDIA_DIR)
            ]
        else:
            cmd = [
                sys.executable, "-m", "manim",
                settings.MANIM_QUALITY,
                str(scene_file),
                scene_name,
                "--media_dir", str(settings.MEDIA_DIR)
            ]
        print(f"Executing native render: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                cwd=str(settings.ROOT_DIR),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=settings.RENDER_TIMEOUT
            )

            if result.returncode != 0:
                print(f"Render failed with code {result.returncode}:\n{result.stderr}")
                return {
                    "status": "failed",
                    "error": result.stderr,
                    "stdout": result.stdout,
                    "code": code
                }

            # Locate the generated MP4 (excluding partial chunks, preferring highest resolution)
            expected_dir = settings.VIDEOS_DIR / f"scene_{task_id}"
            candidates = list(expected_dir.glob(f"**/{scene_name}.mp4")) or list(expected_dir.glob("**/*.mp4"))
            mp4_files = [f for f in candidates if "partial_movie_files" not in str(f)]

            if mp4_files:
                mp4_files.sort(key=lambda p: ("1080p" in str(p), "720p" in str(p), p.stat().st_mtime), reverse=True)
                rel_path = mp4_files[0].relative_to(settings.ROOT_DIR).as_posix()
                print(f"Video generated successfully at: {rel_path}")

                # Manage disk space: delete partial chunks and enforce media retention policy
                from app.services.pruner import cleanup_task_intermediates, prune_old_media
                cleanup_task_intermediates(task_id)
                prune_old_media()

                return {
                    "status": "completed",
                    "video_path": rel_path,
                    "stdout": result.stdout,
                    "code": code,
                    "prompt": problem_prompt
                }
            else:
                return {
                    "status": "failed",
                    "error": "Render succeeded but MP4 file was not found in expected directory.",
                    "stdout": result.stdout,
                    "code": code
                }

        except subprocess.TimeoutExpired:
            return {"status": "failed", "error": f"Rendering timed out after {settings.RENDER_TIMEOUT}s."}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    # 2. Docker Rendering (if explicitly configured)
    abs_scenes_dir = settings.SCENES_DIR.resolve()
    abs_output_dir = settings.MEDIA_DIR.resolve()
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{abs_scenes_dir}:/app/scenes",
        "-v", f"{abs_output_dir}:/app/media",
        "mathanim-renderer",
        "manim", settings.MANIM_QUALITY, f"/app/scenes/scene_{task_id}.py", scene_name,
        "--media_dir", "/app/media"
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=settings.RENDER_TIMEOUT
        )
        if result.returncode != 0:
            return {"status": "failed", "error": result.stderr, "stdout": result.stdout}

        # Locate the generated MP4
        expected_dir = settings.VIDEOS_DIR / f"scene_{task_id}"
        candidates = list(expected_dir.glob(f"**/{scene_name}.mp4")) or list(expected_dir.glob("**/*.mp4"))
        mp4_files = [f for f in candidates if "partial_movie_files" not in str(f)]
        if mp4_files:
            mp4_files.sort(key=lambda p: ("1080p" in str(p), "720p" in str(p), p.stat().st_mtime), reverse=True)
            rel_path = mp4_files[0].relative_to(settings.ROOT_DIR).as_posix()
        else:
            rel_path = f"media/videos/scene_{task_id}/1080p60/{scene_name}.mp4"

        # Manage disk space
        from app.services.pruner import cleanup_task_intermediates, prune_old_media
        cleanup_task_intermediates(task_id)
        prune_old_media()

        return {
            "status": "completed",
            "video_path": rel_path,
            "stdout": result.stdout,
            "code": code,
            "prompt": problem_prompt
        }
    except Exception as e:
        return {"status": "failed", "error": str(e)}


# Celery task wrapper if Celery is available
if celery_app:
    @celery_app.task(bind=True)
    def solve_and_render(self, problem: str, task_id: str):
        return solve_and_render_core(problem, task_id)
else:
    solve_and_render = solve_and_render_core

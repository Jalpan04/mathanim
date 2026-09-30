import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")


class Settings:
    ROOT_DIR: Path = ROOT_DIR
    SCENES_DIR: Path = ROOT_DIR / "generated_scenes"
    MEDIA_DIR: Path = ROOT_DIR / "media"
    VIDEOS_DIR: Path = ROOT_DIR / "media" / "videos"
    CHROMA_DIR: Path = ROOT_DIR / "chroma_db"
    TEMPLATES_DIR: Path = ROOT_DIR / "app" / "templates"
    CURRICULUM_PATH: Path = ROOT_DIR / "curriculum" / "topics.yaml"

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto").lower()  # auto, openai, gemini, anthropic, ollama
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")

    # Renderer Settings
    # "native" executes local manim on the host (fast, no Docker required)
    # "docker" executes inside mathanim-renderer container
    RENDER_MODE: str = os.getenv("RENDER_MODE", "native").lower()
    MANIM_QUALITY: str = os.getenv("MANIM_QUALITY", "-ql")  # -ql (480p15), -qm (720p30), -qh (1080p60)
    RENDER_TIMEOUT: int = int(os.getenv("RENDER_TIMEOUT", "180"))

    # Celery / Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


settings = Settings()

# Ensure critical runtime directories exist
settings.SCENES_DIR.mkdir(parents=True, exist_ok=True)
settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
settings.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# MathAnim

**MathAnim** is an autonomous visualization engine that transforms static mathematical problems into dynamic, step-by-step video tutorials using Manim and an LLM Agent Swarm.

---

## Architecture

- **LangGraph Agents**: Multi-agent swarm (Mathematician, Architect, Developer, Critic) coordinates mathematical solving and animation code synthesis.
- **RAG & Vector Memory (ChromaDB)**: Retrieves official Manim documentation snippets and memorizes 5-star solutions for instant recall.
- **Resilient Multi-Provider LLM Engine**: Automatically uses Cloud API (OpenAI, Gemini, etc.) if configured, with instant zero-downtime fallback to local GPU-accelerated Ollama (`qwen2.5-coder:7b`).
- **High-Performance Native Renderer**: Direct execution using local Manim Community and MiKTeX with optional Docker sandbox support.
- **Modern Web Studio**: Glassmorphism dark-mode UI with live pipeline step tracking, preset math pills, and code preview.

---

## Quick Start

### 1. Requirements

- Python 3.10+ (Poetry managed)
- Manim Community and FFmpeg
- MiKTeX or TeX Live for LaTeX mathematical notation
- NVIDIA GPU (RTX series recommended for Ollama)
- Ollama with `qwen2.5-coder:7b` (for local inference)

### 2. Configuration (.env)

Create or update `.env` in the project root:

```env
# AI Model Selection (auto, ollama, openai, etc.)
LLM_PROVIDER=auto
OLLAMA_MODEL=qwen2.5-coder:7b
OLLAMA_BASE_URL=http://localhost:11434

# Optional: Cloud API Key for ultra-fast generation
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini

# Rendering Configuration (native or docker)
RENDER_MODE=native
MANIM_QUALITY=-ql
```

### 3. Run Web Studio

Start the FastAPI server:

```bash
poetry run python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at `http://127.0.0.1:8000` to access the MathAnim AI Video Studio.

---

## Testing

Run the automated integration test suite:

```bash
poetry run python -m unittest tests/test_integration.py
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

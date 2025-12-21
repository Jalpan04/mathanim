# MathAnim

**MathAnim** is an autonomous visualization engine that transforms static mathematical problems into dynamic, step-by-step video tutorials using Manim.

## Architecture

- **LangGraph Agents**: Orchestrates the reasoning and code generation.
- **RAG (ChromaDB)**: Retrieves relevant Manim documentation.
- **Celery + Redis**: Background rendering of videos.
- **Docker**: Sandboxed execution of generated code.

## Getting Started

1.  **Install Dependencies**:
    ```bash
    poetry install
    ```

2.  **Run Services**:
    ```bash
    docker-compose up -d
    ```

3.  **Start API**:
    ```bash
    poetry run uvicorn app.api.main:app --reload
    ```

4.  **Start Worker**:
    ```bash
    poetry run celery -A workers.celery_app worker --loglevel=info
    ```

from typing import TypedDict, List, Optional


class GraphState(TypedDict):
    """
    Represents the state of the MathAnim LangGraph pipeline.
    """
    user_input: str
    math_solution: str
    retrieved_docs: List[str]
    manim_code: str
    error_log: Optional[str]
    attempt_count: int
    video_path: Optional[str]
    task_id: str
    proven_code: Optional[str]

    # Extended fields for hybrid routing
    archetype: Optional[str]       # e.g. "graphing", "geometry", "calculus"
    topic_id: Optional[int]        # e.g. 20 (matched from curriculum)
    render_errors: List[str]       # Pre-flight validation errors

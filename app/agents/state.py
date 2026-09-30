from typing import TypedDict, List, Optional


class GraphState(TypedDict, total=False):
    """
    Represents the state of the MathAnim LangGraph pipeline.
    """
    user_input: str
    math_solution: Optional[str]
    retrieved_docs: Optional[List[str]]
    manim_code: Optional[str]
    error_log: Optional[str]
    attempt_count: int
    video_path: Optional[str]
    task_id: Optional[str]
    proven_code: Optional[str]
    archetype: Optional[str]
    reference_template: Optional[str]
    template_code: Optional[str]
    render_errors: Optional[List[str]]

from typing import TypedDict, List, Optional

class GraphState(TypedDict):
    """
    Represents the state of the MathAnim graph.
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

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ProblemRequest(BaseModel):
    problem: str = Field(..., description="The math problem to visualize.", example="Graph the function y = sin(x) from 0 to 2*pi")


class JobResponse(BaseModel):
    task_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    task_id: str
    status: str
    video_url: Optional[str] = None
    info: Optional[str] = None
    code: Optional[str] = None
    math_solution: Optional[str] = None


class RatingRequest(BaseModel):
    task_id: str
    rating: int


class SystemStatus(BaseModel):
    llm_provider: str
    active_model: str
    render_mode: str
    gpu_available: bool

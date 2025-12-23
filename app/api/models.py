from pydantic import BaseModel, Field
from typing import Optional, List

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

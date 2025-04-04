from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Task(BaseModel):
    supervisor_id: str  # Converted to ObjectId in service layer
    description: str
    required_skills: List[str]
    due_date: datetime
    start_date: datetime
    assigned_to: Optional[str] = None  # Converted to ObjectId if present
    status: str = "pending"

    class Config:
        from_attributes = True
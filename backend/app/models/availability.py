from pydantic import BaseModel
from datetime import datetime

class Availability(BaseModel):
    user_id: str  # Converted to ObjectId in service layer
    available_from: datetime
    available_to: datetime

    class Config:
        from_attributes = True
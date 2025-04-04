from pydantic import BaseModel

class Skill(BaseModel):
    user_id: str  # Converted to ObjectId in service layer
    skill_name: str
    proficiency_level: int

    class Config:
        from_attributes = True
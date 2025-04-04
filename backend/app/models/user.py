from pydantic import BaseModel, EmailStr
from typing import Literal

class User(BaseModel):
    clerk_id: str
    role: Literal["supervisor", "employee"]
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
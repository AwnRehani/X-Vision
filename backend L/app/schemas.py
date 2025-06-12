# app/schemas.py

from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class PredictOut(BaseModel):
    label: str
    confidence: float
    boxes: List[List[float]]          # Each box is [x1, y1, x2, y2]
    annotated_image_url: Optional[str]

class PredictOutWithReport(PredictOut):
    report: Optional[str]             # LLM-generated text or None

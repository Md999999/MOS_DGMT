from pydantic import BaseModel
from typing import List, Optional

class EmergencyContact(BaseModel):
    name: str
    phone: str
    relationship: str

class SOSRequest(BaseModel):
    message: str

class SOSEvent(BaseModel):
    message: str
    timestamp: str

class UserProfile(BaseModel):
    age: int
    blood_group: str
    health_conditions: List[str]
    allergy: List[str]

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    username: str
    full_name: Optional[str] = None
    email_verified: bool

    class Config:
        orm_mode = True

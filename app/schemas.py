from pydantic import BaseModel
from typing import List

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
    age:int
    blood_group: str
    health_conditions: List[str]
    allergy: List[str]

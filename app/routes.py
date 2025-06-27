from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Dict, List
from app.models import EmergencyContact, SOSRequest, SOSEvent, UserProfile
from app.auth import get_current_user
from app.utils import success_response,error_response
from app.storage import InMemoryStorage
import logging
import re


logger= logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

@router.post("/contacts")
def add_contact(contact: EmergencyContact, username: str = Depends(get_current_user)):
    if not re.fullmatch(r"\+?\d{10,15}", contact.phone):
        raise HTTPException(status_code=400, detail=error_response("Invalid phone number"))
    contacts= InMemoryStorage.contacts.setdefault(username, [])
    if any(c.phone == contact.phone for c in contacts):
        raise HTTPException(status_code=400, detail=error_response("Contact already exists"))
    
    contacts.append(contact)
    return success_response("Contact Added")

@router.get("/contacts", response_model=List[EmergencyContact])
def get_contacts(username: str = Depends(get_current_user)):
    return InMemoryStorage.contacts.get(username, [])

@router.post("/sos")
def send_sos(sos: SOSRequest, username: str = Depends(get_current_user)):
    if not sos.message.strip():
        raise HTTPException(status_code=400, detail=error_response("SOS message can not be empty"))
    event = {
        "message": sos.message,
        "timestamp": datetime.utcnow().isoformat()
    }
    InMemoryStorage.sos_logs.setdefault(username,[]).append(event)
    alerts = []
    for contact in InMemoryStorage.contacts.get(username, []):
        alert = {
            "to": contact.name,
            "phone": contact.phone,
            "relationship": contact.relationship,
            "alert_message": f"ALERT! {username} triggered an SOS: '{sos.message}'"
        }
        logger.info(f"Dispatching alert: {alert}")
        alerts.append(alert)

    return success_response("SOS sent", {"sos_event": event, "dispatched_alerts": alerts})

@router.get("/sos", response_model=List[SOSEvent])
def get_sos_logs(username: str = Depends(get_current_user)):
    return InMemoryStorage.sos_logs.get(username, [])

@router.post("/profile")
def update_profile(profile: UserProfile, username : str = Depends(get_current_user)):
    InMemoryStorage.profiles[username] = profile
    return success_response("Profile updated")

@router.get("/profile", response_model=UserProfile)
def get_profile(username: str =Depends(get_current_user)):
    profile = InMemoryStorage.profiles.get(username)
    if profile is None:
        raise HTTPException(404,"Profile not found")
    return profile

@router.post("/sos/cancel")
def cancel_sos(username: str = Depends(get_current_user)):
    if not InMemoryStorage.sos_logs.get(username):
        raise HTTPException(404,"No SOS event to cancel")
    last_sos = InMemoryStorage.sos_logs[username].pop()
    return success_response("Last SOS event canceled.", {"canceled_sos": last_sos})

def is_admin(username : str) -> bool:
    return username == "admin"

@router.get("/admin/sos", response_model=Dict[str,List[SOSEvent]])
def view_all_sos(username: str = Depends(get_current_user)):
    if not is_admin(username):
        raise HTTPException(403, "Not Authorised")
    return InMemoryStorage.sos_logs

@router.get("/admin/users", response_model=Dict[str, UserProfile])
def view_all_users(username : str = Depends(get_current_user)):
    if not is_admin(username):
        raise HTTPException(403, "Not authorized")
    return InMemoryStorage.profiles
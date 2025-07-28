from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict
from app.schemas import EmergencyContact, SOSRequest, SOSEvent, UserProfile
from app.auth import get_current_user
from app.database import get_db
from app.models import EmergencyContact as EmergencyContactModel, SOSLog, UserProfile as UserProfileModel, User
from app.utils import success_response, error_response
import re

router = APIRouter()

phone_regex = re.compile(r"^\+234\d{10}$")

@router.get("/")
def home():
    return {"message": "SOS Alert API"}

@router.get("/contacts", response_model=List[EmergencyContact])
def get_contacts(user=Depends(get_current_user), db: Session = Depends(get_db)):
    contacts = db.query(EmergencyContactModel).filter(EmergencyContactModel.user_id == user.id).all()
    return contacts

@router.post("/contacts")
def add_contact(contact: EmergencyContact, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if not phone_regex.match(contact.phone):
        raise HTTPException(status_code=400, detail=error_response("Invalid phone number format"))
    exists = db.query(EmergencyContactModel).filter(
        EmergencyContactModel.user_id == user.id,
        EmergencyContactModel.phone == contact.phone
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail=error_response("Contact already exists"))
    new_contact = EmergencyContactModel(
        user_id=user.id,
        name=contact.name,
        phone=contact.phone,
        relationship=contact.relationship,
    )
    db.add(new_contact)
    db.commit()
    return success_response("Contact Added")

@router.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    contact = db.query(EmergencyContactModel).filter(
        EmergencyContactModel.id == contact_id,
        EmergencyContactModel.user_id == user.id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail=error_response("Contact not found"))
    db.delete(contact)
    db.commit()
    return success_response("Contact Deleted")

@router.post("/sos")
def sos_alert(sos: SOSRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # Save SOS to DB
    new_log = SOSLog(user_id=user.id, message=sos.message, timestamp=datetime.utcnow())
    db.add(new_log)
    db.commit()
    # Here you can add notification dispatch logic e.g. SMS/Email to contacts
    return success_response("SOS sent successfully")

@router.get("/sos", response_model=List[SOSEvent])
def get_sos_logs(user=Depends(get_current_user), db: Session = Depends(get_db)):
    logs = db.query(SOSLog).filter(SOSLog.user_id == user.id).all()
    return [{"message": log.message, "timestamp": log.timestamp.isoformat()} for log in logs]

@router.get("/profile", response_model=UserProfile)
def get_profile(user=Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=error_response("Profile not found"))
    return UserProfile(
        age=profile.age,
        blood_group=profile.blood_group,
        health_conditions=profile.health_conditions.split(",") if profile.health_conditions else [],
        allergy=profile.allergy.split(",") if profile.allergy else []
    )

@router.post("/profile")
def update_profile(profile: UserProfile, user=Depends(get_current_user), db: Session = Depends(get_db)):
    existing_profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user.id).first()
    if existing_profile:
        existing_profile.age = profile.age
        existing_profile.blood_group = profile.blood_group
        existing_profile.health_conditions = ",".join(profile.health_conditions)
        existing_profile.allergy = ",".join(profile.allergy)
    else:
        new_profile = UserProfileModel(
            user_id=user.id,
            age=profile.age,
            blood_group=profile.blood_group,
            health_conditions=",".join(profile.health_conditions),
            allergy=",".join(profile.allergy),
        )
        db.add(new_profile)
    db.commit()
    return success_response("Profile updated")

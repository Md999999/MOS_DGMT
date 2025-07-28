from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    email_verified = Column(Boolean, default=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    contacts = relationship("EmergencyContact", back_populates="user")
    profiles = relationship("UserProfile", back_populates="user", uselist=False)
    sos_logs = relationship("SOSLog", back_populates="user")

class EmergencyContact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    phone = Column(String)
    relationship = Column(String)
    user = relationship("User", back_populates="contacts")

class SOSLog(Base):
    __tablename__ = "sos_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="sos_logs")

class UserProfile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    age = Column(Integer)
    blood_group = Column(String)
    health_conditions = Column(Text)
    allergy = Column(Text)
    user = relationship("User", back_populates="profiles")

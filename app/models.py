from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Existing User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)

    # Add this line
    logs = relationship("WeatherLog", back_populates="user", cascade="all, delete-orphan")

# ✅ New WeatherLog model
class WeatherLog(Base):
    __tablename__ = "weather_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Link to User
    temperature = Column(Float)
    humidity = Column(Float)
    condition = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Add this line
    user = relationship("User", back_populates="logs")

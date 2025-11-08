from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    date_of_birth = Column(Date)
    profile_image = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")
    
    # Relationships
    accounts = relationship("Account", back_populates="user")
    itineraries = relationship("Itinerary", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.full_name})>"

from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Time, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Itinerary(Base):
    __tablename__ = "itinerary"
    
    itinerary_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user_type_id = Column(Integer)
    trend_id = Column(Integer)
    itinerary_name = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    total_days = Column(Integer)
    total_destinations = Column(Integer, default=0)
    status = Column(String, default="draft")
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="itineraries")
    itinerary_destinations = relationship("ItineraryDestination", back_populates="itinerary")
    
    def __repr__(self):
        return f"<Itinerary(id={self.itinerary_id}, name={self.itinerary_name})>"


class ItineraryDestination(Base):
    __tablename__ = "itinerary_destination"
    
    itinerary_dest_id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itinerary.itinerary_id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("destination.destination_id"), nullable=False)
    day_number = Column(Integer, nullable=False)
    visit_order = Column(Integer, nullable=False)
    start_time = Column(Time)
    end_time = Column(Time)
    duration_minutes = Column(Integer)
    notes = Column(Text)
    
    # Relationships
    itinerary = relationship("Itinerary", back_populates="itinerary_destinations")
    destination = relationship("Destination", back_populates="itinerary_destinations")
    
    def __repr__(self):
        return f"<ItineraryDestination(id={self.itinerary_dest_id}, day={self.day_number})>"

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Destination(Base):
    __tablename__ = "destination"
    
    destination_id = Column(Integer, primary_key=True, index=True)
    destination_name = Column(String, nullable=False, index=True)
    location_address = Column(String)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    destination_type = Column(String)
    popularity_score = Column(Integer, default=0)
    avg_duration = Column(Integer)  # in minutes
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    category_mappings = relationship("DestinationCategoryMapping", back_populates="destination")
    attributes = relationship("DestinationAttribute", back_populates="destination")
    descriptions = relationship("DestinationDescription", back_populates="destination")
    itinerary_destinations = relationship("ItineraryDestination", back_populates="destination")
    
    def __repr__(self):
        return f"<Destination(id={self.destination_id}, name={self.destination_name})>"


class DestinationCategory(Base):
    __tablename__ = "destination_category"
    
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, nullable=False, unique=True)
    category_description = Column(Text)
    icon = Column(String)
    
    # Relationships
    category_mappings = relationship("DestinationCategoryMapping", back_populates="category")
    
    def __repr__(self):
        return f"<DestinationCategory(id={self.category_id}, name={self.category_name})>"


class DestinationCategoryMapping(Base):
    __tablename__ = "destination_category_mapping"
    
    mapping_id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destination.destination_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("destination_category.category_id"), nullable=False)
    
    # Relationships
    destination = relationship("Destination", back_populates="category_mappings")
    category = relationship("DestinationCategory", back_populates="category_mappings")
    
    def __repr__(self):
        return f"<DestinationCategoryMapping(destination_id={self.destination_id}, category_id={self.category_id})>"


class DestinationAttribute(Base):
    __tablename__ = "destination_attribute"
    
    attribute_id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destination.destination_id"), nullable=False)
    attribute_key = Column(String, nullable=False)
    attribute_value = Column(String)
    attribute_type = Column(String)
    
    # Relationships
    destination = relationship("Destination", back_populates="attributes")
    
    def __repr__(self):
        return f"<DestinationAttribute(id={self.attribute_id}, key={self.attribute_key})>"


class DestinationDescription(Base):
    __tablename__ = "destination_description"
    
    description_id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destination.destination_id"), nullable=False)
    language_code = Column(String(5), default="en")
    title = Column(String)
    short_description = Column(Text)
    full_description = Column(Text)
    history_info = Column(Text)
    cultural_info = Column(Text)
    travel_tips = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    destination = relationship("Destination", back_populates="descriptions")
    
    def __repr__(self):
        return f"<DestinationDescription(id={self.description_id}, lang={self.language_code})>"

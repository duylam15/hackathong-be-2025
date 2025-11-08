from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, JSON, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class Destination(Base):
    """
    Model Destination theo cấu trúc của destinations_data.json
    Đã loại bỏ các bảng phụ phức tạp, tích hợp trực tiếp vào model chính
    """
    __tablename__ = "destination"
    
    # Primary fields từ destinations_data.json
    destination_id = Column(Integer, primary_key=True, index=True)
    destination_name = Column(String, nullable=False, index=True)
    destination_type = Column(String)  # Cultural, Budget, Relaxation, Adventure
    tags = Column(ARRAY(String), default=[])  # ["history", "culture", "architecture", ...]
    
    # Location fields
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    location_address = Column(String)
    
    # Visit information
    price = Column(Integer, default=0)  # Giá vé (VNĐ)
    opening_hours = Column(String)  # "08:00-17:00"
    visit_time = Column(Integer)  # Thời gian tham quan (phút)
    
    # Facilities & extra info
    facilities = Column(ARRAY(String), default=[])  # ["parking", "restroom", "wifi", ...]
    extra_info = Column(JSON, default={})  # {"rating": 4.6, "reviews": 8500} - renamed from 'metadata' to avoid SQLAlchemy conflict
    
    # Audit fields
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships - chỉ giữ relationship với ItineraryDestination
    itinerary_destinations = relationship("ItineraryDestination", back_populates="destination")
    
    def __repr__(self):
        return f"<Destination(id={self.destination_id}, name={self.destination_name}, type={self.destination_type})>"
    
    def to_dict(self):
        """Convert model to dictionary for tour optimizer"""
        return {
            'id': self.destination_id,
            'name': self.destination_name,
            'type': self.destination_type,
            'tags': self.tags or [],
            'latitude': float(self.latitude) if self.latitude else 0,
            'longitude': float(self.longitude) if self.longitude else 0,
            'location_address': self.location_address,
            'price': self.price or 0,
            'opening_hours': self.opening_hours,
            'visit_time': self.visit_time or 60,
            'facilities': self.facilities or [],
            'metadata': self.extra_info or {},  # Map extra_info back to 'metadata' for compatibility
            'is_active': self.is_active
        }

from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class VisitLog(Base):
    """
    Track actual visits and time spent at destinations
    Implicit feedback: visits and duration indicate interest level
    """
    __tablename__ = "visit_log"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destination.destination_id", ondelete="CASCADE"), nullable=False, index=True)
    visit_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer)  # Time spent at location
    completed = Column(Boolean, default=True)  # Did user actually visit or just planned?
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="visits")
    destination = relationship("Destination", backref="visited_by")
    
    def __repr__(self):
        return f"<VisitLog(user={self.user_id}, dest={self.destination_id}, date={self.visit_date})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'destination_id': self.destination_id,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'duration_minutes': self.duration_minutes,
            'completed': self.completed,
            'created_date': self.created_date.isoformat() if self.created_date else None,
        }

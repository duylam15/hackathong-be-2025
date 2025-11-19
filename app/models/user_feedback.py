from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class UserFeedback(Base):
    """
    Track user interactions with recommendations
    Implicit feedback: clicks, skips, shares indicate preferences
    """
    __tablename__ = "user_feedback"
    
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destination.destination_id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(50), nullable=False, index=True)  # 'click', 'skip', 'save', 'share', 'view_details'
    context = Column(JSON)  # {"source": "recommendation", "position": 3, "query": "cultural", "tour_id": 123}
    created_date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", backref="feedback")
    destination = relationship("Destination", backref="feedback_received")
    
    def __repr__(self):
        return f"<UserFeedback(user={self.user_id}, dest={self.destination_id}, action={self.action})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'feedback_id': self.feedback_id,
            'user_id': self.user_id,
            'destination_id': self.destination_id,
            'action': self.action,
            'context': self.context,
            'created_date': self.created_date.isoformat() if self.created_date else None,
        }

from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class DestinationRating(Base):
    """
    User ratings for destinations
    Explicit feedback: 1-5 stars rating system
    """
    __tablename__ = "destination_rating"
    
    rating_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destination.destination_id", ondelete="CASCADE"), nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    review_text = Column(Text)
    visit_date = Column(DateTime)
    created_date = Column(DateTime, default=datetime.utcnow, index=True)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="ratings")
    destination = relationship("Destination", backref="ratings")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'destination_id', name='unique_user_destination_rating'),
    )
    
    def __repr__(self):
        return f"<DestinationRating(user={self.user_id}, dest={self.destination_id}, rating={self.rating})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'rating_id': self.rating_id,
            'user_id': self.user_id,
            'destination_id': self.destination_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'updated_date': self.updated_date.isoformat() if self.updated_date else None,
        }

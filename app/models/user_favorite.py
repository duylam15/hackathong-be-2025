from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class UserFavorite(Base):
    """
    User favorite/saved destinations
    Implicit feedback: saving to favorites indicates interest
    """
    __tablename__ = "user_favorite"
    
    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("destination.destination_id", ondelete="CASCADE"), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(String)  # Optional: User notes about why they saved this
    
    # Relationships
    user = relationship("User", backref="favorites")
    destination = relationship("Destination", backref="favorited_by")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'destination_id', name='unique_user_favorite'),
    )
    
    def __repr__(self):
        return f"<UserFavorite(user={self.user_id}, dest={self.destination_id})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'favorite_id': self.favorite_id,
            'user_id': self.user_id,
            'destination_id': self.destination_id,
            'notes': self.notes,
            'created_date': self.created_date.isoformat() if self.created_date else None,
        }

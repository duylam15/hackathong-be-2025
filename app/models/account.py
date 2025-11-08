from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Account(Base):
    __tablename__ = "account"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    usename = Column(String, unique=True, index=True, nullable=False)  # Note: typo from original schema
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    status = Column(String, default="active")
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    
    def __repr__(self):
        return f"<Account(id={self.id}, username={self.usename}, role={self.role})>"

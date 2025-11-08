from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Company(Base):
    __tablename__ = "company"
    
    company_id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    address = Column(String)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    registration_date = Column(String)
    status = Column(String, default="active")
    
    # Relationships
    destinations = relationship("Destination", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.company_id}, name={self.company_name})>"

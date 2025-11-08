from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.destination import Destination, DestinationCategory, DestinationDescription
from app.schemas.destination import DestinationCreate, DestinationUpdate


class DestinationService:
    """Service layer for Destination operations"""
    
    @staticmethod
    def get_destination(db: Session, destination_id: int) -> Optional[Destination]:
        """Get destination by ID"""
        return db.query(Destination).filter(
            Destination.destination_id == destination_id,
            Destination.is_active == True
        ).first()
    
    @staticmethod
    def get_destinations(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        destination_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Destination]:
        """Get list of destinations with filters"""
        query = db.query(Destination).filter(Destination.is_active == True)
        
        if destination_type:
            query = query.filter(Destination.destination_type == destination_type)
        
        if search:
            query = query.filter(
                or_(
                    Destination.destination_name.ilike(f"%{search}%"),
                    Destination.location_address.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_popular_destinations(
        db: Session,
        limit: int = 10
    ) -> List[Destination]:
        """Get popular destinations sorted by popularity score"""
        return db.query(Destination).filter(
            Destination.is_active == True
        ).order_by(
            Destination.popularity_score.desc()
        ).limit(limit).all()
    
    @staticmethod
    def create_destination(db: Session, destination_data: DestinationCreate) -> Destination:
        """Create a new destination"""
        db_destination = Destination(**destination_data.model_dump())
        db.add(db_destination)
        db.commit()
        db.refresh(db_destination)
        return db_destination
    
    @staticmethod
    def update_destination(
        db: Session,
        destination_id: int,
        destination_data: DestinationUpdate
    ) -> Optional[Destination]:
        """Update an existing destination"""
        db_destination = db.query(Destination).filter(
            Destination.destination_id == destination_id
        ).first()
        
        if not db_destination:
            return None
        
        update_data = destination_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_destination, field, value)
        
        db.commit()
        db.refresh(db_destination)
        return db_destination
    
    @staticmethod
    def delete_destination(db: Session, destination_id: int) -> bool:
        """Soft delete a destination"""
        db_destination = db.query(Destination).filter(
            Destination.destination_id == destination_id
        ).first()
        
        if not db_destination:
            return False
        
        db_destination.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_destinations_by_category(
        db: Session,
        category_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Destination]:
        """Get destinations by category"""
        return db.query(Destination).join(
            Destination.category_mappings
        ).filter(
            Destination.is_active == True,
            Destination.category_mappings.any(category_id=category_id)
        ).offset(skip).limit(limit).all()

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import date
from app.models.itinerary import Itinerary, ItineraryDestination
from app.schemas.itinerary import ItineraryCreate, ItineraryUpdate


class ItineraryService:
    """Service layer for Itinerary operations"""
    
    @staticmethod
    def get_itinerary(db: Session, itinerary_id: int) -> Optional[Itinerary]:
        """Get itinerary by ID"""
        return db.query(Itinerary).filter(
            Itinerary.itinerary_id == itinerary_id
        ).first()
    
    @staticmethod
    def get_user_itineraries(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Itinerary]:
        """Get all itineraries for a user"""
        return db.query(Itinerary).filter(
            Itinerary.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_itinerary(db: Session, itinerary_data: ItineraryCreate) -> Itinerary:
        """Create a new itinerary"""
        db_itinerary = Itinerary(**itinerary_data.model_dump())
        
        # Calculate total days if start and end dates are provided
        if db_itinerary.start_date and db_itinerary.end_date:
            delta = db_itinerary.end_date - db_itinerary.start_date
            db_itinerary.total_days = delta.days + 1
        
        db.add(db_itinerary)
        db.commit()
        db.refresh(db_itinerary)
        return db_itinerary
    
    @staticmethod
    def update_itinerary(
        db: Session,
        itinerary_id: int,
        itinerary_data: ItineraryUpdate
    ) -> Optional[Itinerary]:
        """Update an existing itinerary"""
        db_itinerary = db.query(Itinerary).filter(
            Itinerary.itinerary_id == itinerary_id
        ).first()
        
        if not db_itinerary:
            return None
        
        update_data = itinerary_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_itinerary, field, value)
        
        # Recalculate total days if dates changed
        if db_itinerary.start_date and db_itinerary.end_date:
            delta = db_itinerary.end_date - db_itinerary.start_date
            db_itinerary.total_days = delta.days + 1
        
        db.commit()
        db.refresh(db_itinerary)
        return db_itinerary
    
    @staticmethod
    def delete_itinerary(db: Session, itinerary_id: int) -> bool:
        """Delete an itinerary"""
        db_itinerary = db.query(Itinerary).filter(
            Itinerary.itinerary_id == itinerary_id
        ).first()
        
        if not db_itinerary:
            return False
        
        db.delete(db_itinerary)
        db.commit()
        return True
    
    @staticmethod
    def add_destination_to_itinerary(
        db: Session,
        itinerary_id: int,
        destination_id: int,
        day_number: int,
        visit_order: int,
        **kwargs
    ) -> Optional[ItineraryDestination]:
        """Add a destination to an itinerary"""
        # Check if itinerary exists
        itinerary = db.query(Itinerary).filter(
            Itinerary.itinerary_id == itinerary_id
        ).first()
        
        if not itinerary:
            return None
        
        # Create itinerary destination
        itinerary_dest = ItineraryDestination(
            itinerary_id=itinerary_id,
            destination_id=destination_id,
            day_number=day_number,
            visit_order=visit_order,
            **kwargs
        )
        
        db.add(itinerary_dest)
        
        # Update total destinations count
        itinerary.total_destinations = db.query(ItineraryDestination).filter(
            ItineraryDestination.itinerary_id == itinerary_id
        ).count() + 1
        
        db.commit()
        db.refresh(itinerary_dest)
        return itinerary_dest
    
    @staticmethod
    def remove_destination_from_itinerary(
        db: Session,
        itinerary_dest_id: int
    ) -> bool:
        """Remove a destination from an itinerary"""
        itinerary_dest = db.query(ItineraryDestination).filter(
            ItineraryDestination.itinerary_dest_id == itinerary_dest_id
        ).first()
        
        if not itinerary_dest:
            return False
        
        itinerary_id = itinerary_dest.itinerary_id
        db.delete(itinerary_dest)
        
        # Update total destinations count
        itinerary = db.query(Itinerary).filter(
            Itinerary.itinerary_id == itinerary_id
        ).first()
        
        if itinerary:
            itinerary.total_destinations = db.query(ItineraryDestination).filter(
                ItineraryDestination.itinerary_id == itinerary_id
            ).count()
        
        db.commit()
        return True

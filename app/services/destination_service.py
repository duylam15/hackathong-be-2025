from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.destination import Destination
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
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
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
        
        if tags:
            # Filter by tags (PostgreSQL array contains)
            for tag in tags:
                query = query.filter(Destination.tags.contains([tag]))
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_destinations_by_price_range(
        db: Session,
        min_price: int = 0,
        max_price: int = 10000000,
        skip: int = 0,
        limit: int = 100
    ) -> List[Destination]:
        """Get destinations by price range"""
        return db.query(Destination).filter(
            Destination.is_active == True,
            Destination.price >= min_price,
            Destination.price <= max_price
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_destinations_by_type(
        db: Session,
        destination_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Destination]:
        """Get destinations by type"""
        return db.query(Destination).filter(
            Destination.is_active == True,
            Destination.destination_type == destination_type
        ).offset(skip).limit(limit).all()
    
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
    def bulk_create_from_json(db: Session, destinations_data: List[dict]) -> List[Destination]:
        """Bulk create destinations from JSON data (e.g., destinations_data.json)"""
        created = []
        for data in destinations_data:
            # Map JSON fields to model fields
            destination = Destination(
                destination_id=data.get('id'),
                destination_name=data.get('name'),
                destination_type=data.get('type'),
                tags=data.get('tags', []),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                location_address=data.get('location_address'),
                price=data.get('price', 0),
                opening_hours=data.get('opening_hours'),
                visit_time=data.get('visit_time', 60),
                facilities=data.get('facilities', []),
                extra_info=data.get('metadata', {}),  # Map 'metadata' from JSON to 'extra_info' in model
                is_active=data.get('is_active', True)
            )
            db.add(destination)
            created.append(destination)
        
        db.commit()
        return created

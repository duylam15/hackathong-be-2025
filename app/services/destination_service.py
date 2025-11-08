from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from app.models.destination import Destination
from app.schemas.destination import DestinationCreate, DestinationUpdate, DestinationFilter


class DestinationService:
    """Service layer for Destination operations"""
    
    @staticmethod
    def get_destination(db: Session, destination_id: int) -> Optional[Destination]:
        """Get destination by ID"""
        return db.query(Destination).filter(
            Destination.destination_id == destination_id
        ).first()
    
    @staticmethod
    def get_destinations_with_filters(
        db: Session,
        filters: DestinationFilter,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "destination_id",
        sort_order: str = "asc"
    ) -> Tuple[List[Destination], int]:
        """
        Get destinations with advanced filters and pagination
        
        Returns:
            Tuple[List[Destination], int]: (destinations, total_count)
        """
        query = db.query(Destination)
        
        # Apply filters
        if filters.destination_type:
            query = query.filter(Destination.destination_type == filters.destination_type)
        
        if filters.tags:
            # Filter by tags - destination must have ALL specified tags
            for tag in filters.tags:
                query = query.filter(Destination.tags.contains([tag]))
        
        if filters.min_price is not None:
            query = query.filter(Destination.price >= filters.min_price)
        
        if filters.max_price is not None:
            query = query.filter(Destination.price <= filters.max_price)
        
        if filters.facilities:
            # Filter by facilities - destination must have ALL specified facilities
            for facility in filters.facilities:
                query = query.filter(Destination.facilities.contains([facility]))
        
        if filters.is_active is not None:
            query = query.filter(Destination.is_active == filters.is_active)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Destination.destination_name.ilike(search_term),
                    Destination.location_address.ilike(search_term)
                )
            )
        
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting
        if hasattr(Destination, sort_by):
            order_column = getattr(Destination, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        # Apply pagination
        skip = (page - 1) * page_size
        destinations = query.offset(skip).limit(page_size).all()
        
        return destinations, total
    
    @staticmethod
    def get_destinations(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        destination_type: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Destination]:
        """Get list of destinations with basic filters (deprecated - use get_destinations_with_filters)"""
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
            for tag in tags:
                query = query.filter(Destination.tags.contains([tag]))
        
        return query.offset(skip).limit(limit).all()
    
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

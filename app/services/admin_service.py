from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
from app.models.destination import Destination
from app.schemas.destination import (
    DestinationCreate, 
    DestinationUpdate, 
    DestinationFilter,
)
import logging

logger = logging.getLogger(__name__)


class AdminDestinationService:
    """Admin service for Destination management with full CRUD operations"""
    
    @staticmethod
    def search_destinations(
        db: Session,
        destination_type: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        facilities: Optional[List[str]] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        is_active: Optional[bool] = True,
        sort_by: str = "destination_id",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Destination], int, Dict[str, Any]]:
        """
        Search destinations with advanced filters and pagination
        
        Args:
            db: Database session
            destination_type: Filter by type (Cultural, Budget, Relaxation, Adventure, Family)
            search: Search in name and address
            tags: Filter by tags (must have ALL specified tags)
            facilities: Filter by facilities (must have ALL specified facilities)
            min_price: Minimum price
            max_price: Maximum price
            is_active: Filter by active status
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            page: Page number (starting from 1)
            page_size: Items per page
            
        Returns:
            Tuple[List[Destination], int, Dict]: (destinations, total_count, pagination_info)
        """
        try:
            query = db.query(Destination)
            
            # Apply filters
            if destination_type:
                query = query.filter(Destination.destination_type == destination_type)
            
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Destination.destination_name.ilike(search_term),
                        Destination.location_address.ilike(search_term)
                    )
                )
            
            if tags:
                for tag in tags:
                    query = query.filter(Destination.tags.contains([tag]))
            
            if facilities:
                for facility in facilities:
                    query = query.filter(Destination.facilities.contains([facility]))
            
            if min_price is not None:
                query = query.filter(Destination.price >= min_price)
            
            if max_price is not None:
                query = query.filter(Destination.price <= max_price)
            
            if is_active is not None:
                query = query.filter(Destination.is_active == is_active)
            
            # Get total count before pagination
            total = query.count()
            
            # Apply sorting
            if hasattr(Destination, sort_by):
                order_column = getattr(Destination, sort_by)
                if sort_order.lower() == "desc":
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column.asc())
            else:
                # Default sort by destination_id
                query = query.order_by(Destination.destination_id.asc())
            
            # Apply pagination
            skip = (page - 1) * page_size
            destinations = query.offset(skip).limit(page_size).all()
            
            # Calculate pagination info
            total_pages = (total + page_size - 1) // page_size
            pagination_info = {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
            
            logger.info(f"Search destinations: found {total} results, returning page {page}/{total_pages}")
            return destinations, total, pagination_info
            
        except Exception as e:
            logger.error(f"Error searching destinations: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error searching destinations: {str(e)}"
            )
    
    @staticmethod
    def get_destination_by_id(db: Session, destination_id: int) -> Destination:
        """
        Get destination by ID
        
        Args:
            db: Database session
            destination_id: Destination ID
            
        Returns:
            Destination object
            
        Raises:
            HTTPException: 404 if destination not found
        """
        try:
            destination = db.query(Destination).filter(
                Destination.destination_id == destination_id
            ).first()
            
            if not destination:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Destination with ID {destination_id} not found"
                )
            
            logger.info(f"Retrieved destination: {destination.destination_name} (ID: {destination_id})")
            return destination
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting destination {destination_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving destination: {str(e)}"
            )
    
    @staticmethod
    def create_destination(db: Session, destination_data: DestinationCreate) -> Destination:
        """
        Create a new destination
        
        Args:
            db: Database session
            destination_data: Destination creation data
            
        Returns:
            Created Destination object
            
        Raises:
            HTTPException: 400 if validation fails, 500 if creation fails
        """
        try:
            # Validate required fields
            if not destination_data.destination_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Destination name is required"
                )
            
            # Validate price
            if destination_data.price is not None and destination_data.price < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Price cannot be negative"
                )
            
            # Validate coordinates
            if destination_data.latitude is not None:
                if destination_data.latitude < -90 or destination_data.latitude > 90:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Latitude must be between -90 and 90"
                    )
            
            if destination_data.longitude is not None:
                if destination_data.longitude < -180 or destination_data.longitude > 180:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Longitude must be between -180 and 180"
                    )
            
            # Create destination
            db_destination = Destination(**destination_data.model_dump())
            db.add(db_destination)
            db.commit()
            db.refresh(db_destination)
            
            logger.info(f"Created destination: {db_destination.destination_name} (ID: {db_destination.destination_id})")
            return db_destination
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating destination: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating destination: {str(e)}"
            )
    
    @staticmethod
    def update_destination(
        db: Session,
        destination_id: int,
        destination_data: DestinationUpdate
    ) -> Destination:
        """
        Update an existing destination
        
        Args:
            db: Database session
            destination_id: Destination ID to update
            destination_data: Updated destination data
            
        Returns:
            Updated Destination object
            
        Raises:
            HTTPException: 404 if not found, 400 if validation fails, 500 if update fails
        """
        try:
            # Get existing destination
            db_destination = db.query(Destination).filter(
                Destination.destination_id == destination_id
            ).first()
            
            if not db_destination:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Destination with ID {destination_id} not found"
                )
            
            # Validate update data
            update_data = destination_data.model_dump(exclude_unset=True)
            
            if "price" in update_data and update_data["price"] is not None:
                if update_data["price"] < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Price cannot be negative"
                    )
            
            if "latitude" in update_data and update_data["latitude"] is not None:
                if update_data["latitude"] < -90 or update_data["latitude"] > 90:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Latitude must be between -90 and 90"
                    )
            
            if "longitude" in update_data and update_data["longitude"] is not None:
                if update_data["longitude"] < -180 or update_data["longitude"] > 180:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Longitude must be between -180 and 180"
                    )
            
            # Update fields
            for field, value in update_data.items():
                setattr(db_destination, field, value)
            
            db.commit()
            db.refresh(db_destination)
            
            logger.info(f"Updated destination: {db_destination.destination_name} (ID: {destination_id})")
            return db_destination
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating destination {destination_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating destination: {str(e)}"
            )
    
    @staticmethod
    def delete_destination(db: Session, destination_id: int) -> Dict[str, Any]:
        """
        Soft delete a destination (set is_active = False)
        
        Args:
            db: Database session
            destination_id: Destination ID to delete
            
        Returns:
            Dict with success message and deleted destination info
            
        Raises:
            HTTPException: 404 if not found, 500 if deletion fails
        """
        try:
            db_destination = db.query(Destination).filter(
                Destination.destination_id == destination_id
            ).first()
            
            if not db_destination:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Destination with ID {destination_id} not found"
                )
            
            # Check if already deleted
            if not db_destination.is_active:
                logger.warning(f"Destination {destination_id} is already deleted")
                return {
                    "message": "Destination already deleted",
                    "destination_id": destination_id,
                    "destination_name": db_destination.destination_name,
                    "is_active": False
                }
            
            # Soft delete
            db_destination.is_active = False
            db.commit()
            
            logger.info(f"Deleted destination: {db_destination.destination_name} (ID: {destination_id})")
            return {
                "message": "Destination deleted successfully",
                "destination_id": destination_id,
                "destination_name": db_destination.destination_name,
                "is_active": False
            }
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting destination {destination_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting destination: {str(e)}"
            )
    
    @staticmethod
    def restore_destination(db: Session, destination_id: int) -> Destination:
        """
        Restore a soft-deleted destination (set is_active = True)
        
        Args:
            db: Database session
            destination_id: Destination ID to restore
            
        Returns:
            Restored Destination object
        """
        try:
            db_destination = db.query(Destination).filter(
                Destination.destination_id == destination_id
            ).first()
            
            if not db_destination:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Destination with ID {destination_id} not found"
                )
            
            db_destination.is_active = True
            db.commit()
            db.refresh(db_destination)
            
            logger.info(f"Restored destination: {db_destination.destination_name} (ID: {destination_id})")
            return db_destination
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error restoring destination {destination_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error restoring destination: {str(e)}"
            )
    
    @staticmethod
    def get_statistics(db: Session) -> Dict[str, Any]:
        """
        Get destination statistics
        
        Returns:
            Dict with various statistics
        """
        try:
            total = db.query(Destination).count()
            active = db.query(Destination).filter(Destination.is_active == True).count()
            inactive = total - active
            
            # Count by type
            types = db.query(
                Destination.destination_type,
                func.count(Destination.destination_id)
            ).filter(Destination.is_active == True).group_by(
                Destination.destination_type
            ).all()
            
            # Average price
            avg_price = db.query(func.avg(Destination.price)).filter(
                Destination.is_active == True,
                Destination.price.isnot(None)
            ).scalar() or 0
            
            return {
                "total_destinations": total,
                "active_destinations": active,
                "inactive_destinations": inactive,
                "destinations_by_type": {type_name: count for type_name, count in types if type_name},
                "average_price": round(float(avg_price), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting statistics: {str(e)}"
            )

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil
from app.api.deps import get_database
from app.schemas.destination import (
    DestinationCreate, 
    DestinationUpdate, 
    DestinationResponse,
    DestinationListResponse,
    DestinationFilter
)
from app.services.destination_service import DestinationService

router = APIRouter()


@router.get("/search", response_model=DestinationListResponse)
def search_destinations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    destination_type: Optional[str] = Query(None, description="Filter by type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (comma-separated)"),
    min_price: Optional[int] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[int] = Query(None, ge=0, description="Maximum price"),
    facilities: Optional[List[str]] = Query(None, description="Filter by facilities"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name and address"),
    sort_by: str = Query("destination_id", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_database)
):
    """
    Search and filter destinations with pagination
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **destination_type**: Filter by type (Cultural, Budget, Relaxation, Adventure, Family)
    - **tags**: Filter by tags (must have ALL specified tags)
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **facilities**: Filter by facilities (must have ALL specified)
    - **is_active**: Filter by active status
    - **search**: Search in name and address
    - **sort_by**: Sort field (destination_id, destination_name, price, etc.)
    - **sort_order**: Sort order (asc or desc)
    """
    # Build filter object
    filters = DestinationFilter(
        destination_type=destination_type,
        tags=tags,
        min_price=min_price,
        max_price=max_price,
        facilities=facilities,
        is_active=is_active,
        search=search
    )
    
    # Get destinations with filters
    destinations, total = DestinationService.get_destinations_with_filters(
        db=db,
        filters=filters,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Calculate total pages
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    return DestinationListResponse(
        items=destinations,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/", response_model=List[DestinationResponse])
def get_destinations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    destination_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_database)
):
    """
    Get list of destinations (simple version without pagination)
    
    **Deprecated**: Use /search endpoint for better pagination and filtering
    """
    destinations = DestinationService.get_destinations(
        db,
        skip=skip,
        limit=limit,
        destination_type=destination_type,
        search=search
    )
    return destinations


@router.get("/{destination_id}", response_model=DestinationResponse)
def get_destination(
    destination_id: int,
    db: Session = Depends(get_database)
):
    """Get destination by ID"""
    destination = DestinationService.get_destination(db, destination_id=destination_id)
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found"
        )
    return destination


@router.post("/", response_model=DestinationResponse, status_code=status.HTTP_201_CREATED)
def create_destination(
    destination_data: DestinationCreate,
    db: Session = Depends(get_database)
):
    """
    Create a new destination
    
    Required fields:
    - **destination_name**: Name of the destination
    
    Optional fields:
    - **destination_type**: Cultural, Budget, Relaxation, Adventure, Family
    - **tags**: List of tags
    - **location_address**: Address
    - **latitude**, **longitude**: Coordinates
    - **price**: Entrance fee in VNĐ
    - **opening_hours**: Opening hours (e.g., "08:00-17:00")
    - **visit_time**: Recommended visit duration in minutes
    - **facilities**: List of facilities
    - **extra_info**: Additional information (JSON object)
    """
    try:
        destination = DestinationService.create_destination(db, destination_data=destination_data)
        return destination
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create destination: {str(e)}"
        )


@router.put("/{destination_id}", response_model=DestinationResponse)
def update_destination(
    destination_id: int,
    destination_data: DestinationUpdate,
    db: Session = Depends(get_database)
):
    """
    Update an existing destination
    
    All fields are optional - only provided fields will be updated
    """
    destination = DestinationService.update_destination(
        db,
        destination_id=destination_id,
        destination_data=destination_data
    )
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found"
        )
    return destination


@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(
    destination_id: int,
    db: Session = Depends(get_database)
):
    """
    Delete a destination (soft delete - sets is_active to False)
    
    This is a soft delete operation - the destination remains in the database
    but is marked as inactive
    """
    success = DestinationService.delete_destination(db, destination_id=destination_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination with ID {destination_id} not found"
        )
    return None

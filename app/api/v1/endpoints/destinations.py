from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_database
from app.schemas.destination import (
    DestinationCreate, DestinationUpdate, DestinationResponse
)
from app.services.destination_service import DestinationService

router = APIRouter()


@router.get("/", response_model=List[DestinationResponse])
def get_destinations(
    skip: int = 0,
    limit: int = 100,
    destination_type: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_database)
):
    """Get list of destinations with optional filters"""
    destinations = DestinationService.get_destinations(
        db,
        skip=skip,
        limit=limit,
        destination_type=destination_type,
        search=search
    )
    return destinations


@router.get("/popular", response_model=List[DestinationResponse])
def get_popular_destinations(
    limit: int = 10,
    db: Session = Depends(get_database)
):
    """Get popular destinations"""
    destinations = DestinationService.get_popular_destinations(db, limit=limit)
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
            detail="Destination not found"
        )
    return destination


@router.post("/", response_model=DestinationResponse, status_code=status.HTTP_201_CREATED)
def create_destination(
    destination_data: DestinationCreate,
    db: Session = Depends(get_database)
):
    """Create a new destination"""
    destination = DestinationService.create_destination(db, destination_data=destination_data)
    return destination


@router.put("/{destination_id}", response_model=DestinationResponse)
def update_destination(
    destination_id: int,
    destination_data: DestinationUpdate,
    db: Session = Depends(get_database)
):
    """Update an existing destination"""
    destination = DestinationService.update_destination(
        db,
        destination_id=destination_id,
        destination_data=destination_data
    )
    if not destination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    return destination


@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(
    destination_id: int,
    db: Session = Depends(get_database)
):
    """Delete a destination (soft delete)"""
    success = DestinationService.delete_destination(db, destination_id=destination_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Destination not found"
        )
    return None


@router.get("/category/{category_id}", response_model=List[DestinationResponse])
def get_destinations_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database)
):
    """Get destinations by category"""
    destinations = DestinationService.get_destinations_by_category(
        db,
        category_id=category_id,
        skip=skip,
        limit=limit
    )
    return destinations

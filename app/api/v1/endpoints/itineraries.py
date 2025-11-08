from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_database
from app.schemas.itinerary import (
    ItineraryCreate, ItineraryUpdate, ItineraryResponse
)
from app.services.itinerary_service import ItineraryService

router = APIRouter()


@router.get("/user/{user_id}", response_model=List[ItineraryResponse])
def get_user_itineraries(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_database)
):
    """Get all itineraries for a user"""
    itineraries = ItineraryService.get_user_itineraries(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    return itineraries


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def get_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_database)
):
    """Get itinerary by ID"""
    itinerary = ItineraryService.get_itinerary(db, itinerary_id=itinerary_id)
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    return itinerary


@router.post("/", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
def create_itinerary(
    itinerary_data: ItineraryCreate,
    db: Session = Depends(get_database)
):
    """Create a new itinerary"""
    itinerary = ItineraryService.create_itinerary(db, itinerary_data=itinerary_data)
    return itinerary


@router.put("/{itinerary_id}", response_model=ItineraryResponse)
def update_itinerary(
    itinerary_id: int,
    itinerary_data: ItineraryUpdate,
    db: Session = Depends(get_database)
):
    """Update an existing itinerary"""
    itinerary = ItineraryService.update_itinerary(
        db,
        itinerary_id=itinerary_id,
        itinerary_data=itinerary_data
    )
    if not itinerary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    return itinerary


@router.delete("/{itinerary_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_itinerary(
    itinerary_id: int,
    db: Session = Depends(get_database)
):
    """Delete an itinerary"""
    success = ItineraryService.delete_itinerary(db, itinerary_id=itinerary_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    return None


@router.post("/{itinerary_id}/destinations/{destination_id}")
def add_destination_to_itinerary(
    itinerary_id: int,
    destination_id: int,
    day_number: int,
    visit_order: int,
    db: Session = Depends(get_database)
):
    """Add a destination to an itinerary"""
    itinerary_dest = ItineraryService.add_destination_to_itinerary(
        db,
        itinerary_id=itinerary_id,
        destination_id=destination_id,
        day_number=day_number,
        visit_order=visit_order
    )
    if not itinerary_dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary not found"
        )
    return itinerary_dest


@router.delete("/destinations/{itinerary_dest_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_destination_from_itinerary(
    itinerary_dest_id: int,
    db: Session = Depends(get_database)
):
    """Remove a destination from an itinerary"""
    success = ItineraryService.remove_destination_from_itinerary(
        db,
        itinerary_dest_id=itinerary_dest_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Itinerary destination not found"
        )
    return None

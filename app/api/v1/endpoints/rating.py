"""
API Endpoints for Ratings, Favorites, Visits, and Feedback
All endpoints are public (no authentication required)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.rating import (
    RatingCreate, RatingUpdate, RatingResponse,
    FavoriteCreate, FavoriteResponse,
    VisitLogCreate, VisitLogResponse,
    FeedbackCreate, FeedbackResponse
)
from app.services.rating_service import (
    RatingService, FavoriteService, VisitLogService, FeedbackService
)

router = APIRouter()


# =====================================================
# RATING ENDPOINTS
# =====================================================

@router.post("/ratings/", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def create_rating(
    rating_data: RatingCreate,
    db: Session = Depends(get_db)
):
    """
    Rate a destination (1-5 stars) - PUBLIC ENDPOINT
    
    - Creates new rating or updates existing one
    - Automatically updates destination statistics
    - Requires user_id in request body
    """
    return RatingService.create_rating(db, rating_data.user_id, rating_data)


@router.get("/ratings/user/{user_id}", response_model=List[RatingResponse])
def get_user_ratings(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all ratings by a specific user"""
    return RatingService.get_user_ratings(db, user_id, skip, limit)


@router.get("/ratings/destination/{destination_id}", response_model=List[RatingResponse])
def get_destination_ratings(
    destination_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all ratings for a specific destination"""
    return RatingService.get_destination_ratings(db, destination_id, skip, limit)


@router.delete("/ratings/{user_id}/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    user_id: int,
    destination_id: int,
    db: Session = Depends(get_db)
):
    """Delete a rating - PUBLIC ENDPOINT"""
    RatingService.delete_rating(db, user_id, destination_id)
    return None


# =====================================================
# FAVORITE ENDPOINTS
# =====================================================

@router.post("/favorites/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db)
):
    """
    Add destination to favorites - PUBLIC ENDPOINT
    
    - Save destinations you want to visit later
    - Automatically updates destination statistics
    - Requires user_id in request body
    """
    return FavoriteService.add_favorite(db, favorite_data.user_id, favorite_data)


@router.get("/favorites/user/{user_id}", response_model=List[FavoriteResponse])
def get_user_favorites(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all favorites for a specific user - PUBLIC ENDPOINT"""
    return FavoriteService.get_user_favorites(db, user_id, skip, limit)


@router.delete("/favorites/{user_id}/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    user_id: int,
    destination_id: int,
    db: Session = Depends(get_db)
):
    """Remove destination from favorites - PUBLIC ENDPOINT"""
    FavoriteService.remove_favorite(db, user_id, destination_id)
    return None


# =====================================================
# VISIT LOG ENDPOINTS
# =====================================================

@router.post("/visits/", response_model=VisitLogResponse, status_code=status.HTTP_201_CREATED)
def log_visit(
    visit_data: VisitLogCreate,
    db: Session = Depends(get_db)
):
    """
    Log a visit to a destination - PUBLIC ENDPOINT
    
    - Track actual visits with date and duration
    - Used for implicit feedback in collaborative filtering
    - Requires user_id in request body
    """
    return VisitLogService.log_visit(db, visit_data.user_id, visit_data)


@router.get("/visits/user/{user_id}", response_model=List[VisitLogResponse])
def get_user_visits(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all visit logs for a specific user - PUBLIC ENDPOINT"""
    return VisitLogService.get_user_visits(db, user_id, skip, limit)


# =====================================================
# FEEDBACK ENDPOINTS
# =====================================================

@router.post("/feedback/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Track user interaction with destinations - PUBLIC ENDPOINT
    
    - Actions: click, skip, save, share, view_details
    - Used for implicit feedback in collaborative filtering
    - Requires user_id in request body
    """
    return FeedbackService.create_feedback(db, feedback_data.user_id, feedback_data)


@router.get("/feedback/user/{user_id}", response_model=List[FeedbackResponse])
def get_user_feedback(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all feedback entries for a specific user - PUBLIC ENDPOINT"""
    return FeedbackService.get_user_feedback(db, user_id, skip, limit)

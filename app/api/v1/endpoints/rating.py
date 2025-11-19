"""
API Endpoints for Ratings, Favorites, Visits, and Feedback
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rate a destination (1-5 stars)
    
    - Creates new rating or updates existing one
    - Automatically updates destination statistics
    """
    return RatingService.create_rating(db, current_user.id, rating_data)


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


@router.get("/ratings/me", response_model=List[RatingResponse])
def get_my_ratings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all ratings by current authenticated user"""
    return RatingService.get_user_ratings(db, current_user.id, skip, limit)


@router.delete("/ratings/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(
    destination_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a rating"""
    RatingService.delete_rating(db, current_user.id, destination_id)
    return None


# =====================================================
# FAVORITE ENDPOINTS
# =====================================================

@router.post("/favorites/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add destination to favorites
    
    - Save destinations you want to visit later
    - Automatically updates destination statistics
    """
    return FavoriteService.add_favorite(db, current_user.id, favorite_data)


@router.get("/favorites/me", response_model=List[FavoriteResponse])
def get_my_favorites(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all favorites for current user"""
    return FavoriteService.get_user_favorites(db, current_user.id, skip, limit)


@router.delete("/favorites/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    destination_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove destination from favorites"""
    FavoriteService.remove_favorite(db, current_user.id, destination_id)
    return None


# =====================================================
# VISIT LOG ENDPOINTS
# =====================================================

@router.post("/visits/", response_model=VisitLogResponse, status_code=status.HTTP_201_CREATED)
def log_visit(
    visit_data: VisitLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log a visit to a destination
    
    - Track actual visits with date and duration
    - Used for implicit feedback in collaborative filtering
    """
    return VisitLogService.log_visit(db, current_user.id, visit_data)


@router.get("/visits/me", response_model=List[VisitLogResponse])
def get_my_visits(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all visit logs for current user"""
    return VisitLogService.get_user_visits(db, current_user.id, skip, limit)


# =====================================================
# FEEDBACK ENDPOINTS
# =====================================================

@router.post("/feedback/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Track user interaction with destinations
    
    - Actions: click, skip, save, share, view_details
    - Used for implicit feedback in collaborative filtering
    """
    return FeedbackService.create_feedback(db, current_user.id, feedback_data)


@router.get("/feedback/me", response_model=List[FeedbackResponse])
def get_my_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all feedback entries for current user"""
    return FeedbackService.get_user_feedback(db, current_user.id, skip, limit)

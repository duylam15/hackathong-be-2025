from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


# =====================================================
# DESTINATION RATING SCHEMAS
# =====================================================

class RatingCreate(BaseModel):
    """Schema for creating a new rating"""
    destination_id: int = Field(..., gt=0, description="Destination ID to rate")
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating value (1.0 - 5.0)")
    review_text: Optional[str] = Field(None, max_length=2000, description="Optional review text")
    visit_date: Optional[datetime] = Field(None, description="Date of visit")
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination_id": 1,
                "rating": 4.5,
                "review_text": "Tuyệt vời! Kiến trúc đẹp và không gian yên tĩnh.",
                "visit_date": "2025-11-15T10:00:00"
            }
        }


class RatingUpdate(BaseModel):
    """Schema for updating an existing rating"""
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Updated rating")
    review_text: Optional[str] = Field(None, max_length=2000, description="Updated review text")
    visit_date: Optional[datetime] = Field(None, description="Updated visit date")


class RatingResponse(BaseModel):
    """Schema for rating response"""
    rating_id: int
    user_id: int
    destination_id: int
    rating: float
    review_text: Optional[str]
    visit_date: Optional[datetime]
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# USER FAVORITE SCHEMAS
# =====================================================

class FavoriteCreate(BaseModel):
    """Schema for adding a favorite"""
    destination_id: int = Field(..., gt=0, description="Destination ID to favorite")
    notes: Optional[str] = Field(None, max_length=500, description="Optional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination_id": 5,
                "notes": "Muốn đến đây vào mùa xuân"
            }
        }


class FavoriteResponse(BaseModel):
    """Schema for favorite response"""
    favorite_id: int
    user_id: int
    destination_id: int
    notes: Optional[str]
    created_date: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# VISIT LOG SCHEMAS
# =====================================================

class VisitLogCreate(BaseModel):
    """Schema for logging a visit"""
    destination_id: int = Field(..., gt=0, description="Destination ID visited")
    visit_date: datetime = Field(..., description="Date and time of visit")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Duration spent (minutes)")
    completed: bool = Field(True, description="Whether visit was completed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination_id": 3,
                "visit_date": "2025-11-18T14:30:00",
                "duration_minutes": 120,
                "completed": True
            }
        }


class VisitLogResponse(BaseModel):
    """Schema for visit log response"""
    log_id: int
    user_id: int
    destination_id: int
    visit_date: datetime
    duration_minutes: Optional[int]
    completed: bool
    created_date: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# USER FEEDBACK SCHEMAS
# =====================================================

class FeedbackCreate(BaseModel):
    """Schema for creating feedback"""
    destination_id: int = Field(..., gt=0, description="Destination ID")
    action: str = Field(..., description="Action type: click, skip, save, share, view_details")
    context: Optional[dict] = Field(None, description="Additional context")
    
    @validator('action')
    def validate_action(cls, v):
        allowed_actions = ['click', 'skip', 'save', 'share', 'view_details']
        if v not in allowed_actions:
            raise ValueError(f"Action must be one of {allowed_actions}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination_id": 7,
                "action": "click",
                "context": {
                    "source": "recommendation",
                    "position": 2,
                    "tour_id": 123
                }
            }
        }


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    feedback_id: int
    user_id: int
    destination_id: int
    action: str
    context: Optional[dict]
    created_date: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# STATISTICS & ANALYTICS SCHEMAS
# =====================================================

class UserRatingStats(BaseModel):
    """User's rating statistics"""
    user_id: int
    total_ratings: int
    avg_rating_given: float
    most_rated_type: Optional[str]
    rating_distribution: dict  # {1: 2, 2: 5, 3: 10, 4: 25, 5: 15}


class DestinationStats(BaseModel):
    """Destination statistics"""
    destination_id: int
    destination_name: str
    avg_rating: float
    total_ratings: int
    total_visits: int
    total_favorites: int
    popularity_score: float
    last_updated: datetime

"""
Rating & Feedback API Service - Business logic for ratings, favorites, visits, feedback
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from fastapi import HTTPException, status
from datetime import datetime

from app.models.destination_rating import DestinationRating
from app.models.user_favorite import UserFavorite
from app.models.visit_log import VisitLog
from app.models.user_feedback import UserFeedback
from app.models.destination import Destination
from app.models.user import User
from app.schemas.rating import (
    RatingCreate, RatingUpdate,
    FavoriteCreate,
    VisitLogCreate,
    FeedbackCreate
)


class RatingService:
    """Service for managing destination ratings"""
    
    @staticmethod
    def create_rating(db: Session, user_id: int, rating_data: RatingCreate) -> DestinationRating:
        """Create or update a rating"""
        # Check if destination exists
        destination = db.query(Destination).filter(
            Destination.destination_id == rating_data.destination_id,
            Destination.is_active == True
        ).first()
        
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination {rating_data.destination_id} not found"
            )
        
        # Check if user already rated this destination
        existing = db.query(DestinationRating).filter(
            DestinationRating.user_id == user_id,
            DestinationRating.destination_id == rating_data.destination_id
        ).first()
        
        if existing:
            # Update existing rating
            existing.rating = rating_data.rating
            existing.review_text = rating_data.review_text
            existing.visit_date = rating_data.visit_date
            existing.updated_date = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            
            # Update destination stats
            RatingService._update_destination_stats(db, rating_data.destination_id)
            
            return existing
        else:
            # Create new rating
            db_rating = DestinationRating(
                user_id=user_id,
                destination_id=rating_data.destination_id,
                rating=rating_data.rating,
                review_text=rating_data.review_text,
                visit_date=rating_data.visit_date
            )
            db.add(db_rating)
            db.commit()
            db.refresh(db_rating)
            
            # Update destination stats
            RatingService._update_destination_stats(db, rating_data.destination_id)
            
            return db_rating
    
    @staticmethod
    def get_user_ratings(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[DestinationRating]:
        """Get all ratings by a user"""
        return db.query(DestinationRating).filter(
            DestinationRating.user_id == user_id
        ).order_by(desc(DestinationRating.created_date)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_destination_ratings(db: Session, destination_id: int, skip: int = 0, limit: int = 100) -> List[DestinationRating]:
        """Get all ratings for a destination"""
        return db.query(DestinationRating).filter(
            DestinationRating.destination_id == destination_id
        ).order_by(desc(DestinationRating.created_date)).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_rating(db: Session, user_id: int, destination_id: int) -> bool:
        """Delete a rating"""
        rating = db.query(DestinationRating).filter(
            DestinationRating.user_id == user_id,
            DestinationRating.destination_id == destination_id
        ).first()
        
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rating not found"
            )
        
        db.delete(rating)
        db.commit()
        
        # Update destination stats
        RatingService._update_destination_stats(db, destination_id)
        
        return True
    
    @staticmethod
    def _update_destination_stats(db: Session, destination_id: int):
        """Update aggregated statistics for a destination"""
        dest = db.query(Destination).filter(
            Destination.destination_id == destination_id
        ).first()
        
        if not dest:
            return
        
        # Calculate average rating
        rating_stats = db.query(
            func.avg(DestinationRating.rating),
            func.count(DestinationRating.rating_id)
        ).filter(
            DestinationRating.destination_id == destination_id
        ).first()
        
        dest.avg_rating = float(rating_stats[0]) if rating_stats[0] else 0.0
        dest.total_ratings = int(rating_stats[1])
        
        # Calculate visits
        dest.total_visits = db.query(VisitLog).filter(
            VisitLog.destination_id == destination_id,
            VisitLog.completed == True
        ).count()
        
        # Calculate favorites
        dest.total_favorites = db.query(UserFavorite).filter(
            UserFavorite.destination_id == destination_id
        ).count()
        
        # Calculate popularity score (weighted combination)
        dest.popularity_score = (
            0.5 * (dest.avg_rating / 5.0) +
            0.3 * min(dest.total_ratings / 100.0, 1.0) +
            0.2 * min(dest.total_visits / 500.0, 1.0)
        )
        
        dest.last_stats_update = datetime.utcnow()
        db.commit()


class FavoriteService:
    """Service for managing user favorites"""
    
    @staticmethod
    def add_favorite(db: Session, user_id: int, favorite_data: FavoriteCreate) -> UserFavorite:
        """Add destination to favorites"""
        # Check if destination exists
        destination = db.query(Destination).filter(
            Destination.destination_id == favorite_data.destination_id,
            Destination.is_active == True
        ).first()
        
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination {favorite_data.destination_id} not found"
            )
        
        # Check if already favorited
        existing = db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.destination_id == favorite_data.destination_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Destination already in favorites"
            )
        
        # Create favorite
        db_favorite = UserFavorite(
            user_id=user_id,
            destination_id=favorite_data.destination_id,
            notes=favorite_data.notes
        )
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        
        # Update destination stats
        RatingService._update_destination_stats(db, favorite_data.destination_id)
        
        return db_favorite
    
    @staticmethod
    def get_user_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[UserFavorite]:
        """Get all favorites for a user"""
        return db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id
        ).order_by(desc(UserFavorite.created_date)).offset(skip).limit(limit).all()
    
    @staticmethod
    def remove_favorite(db: Session, user_id: int, destination_id: int) -> bool:
        """Remove destination from favorites"""
        favorite = db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.destination_id == destination_id
        ).first()
        
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found"
            )
        
        db.delete(favorite)
        db.commit()
        
        # Update destination stats
        RatingService._update_destination_stats(db, destination_id)
        
        return True


class VisitLogService:
    """Service for logging visits"""
    
    @staticmethod
    def log_visit(db: Session, user_id: int, visit_data: VisitLogCreate) -> VisitLog:
        """Log a visit to a destination"""
        # Check if destination exists
        destination = db.query(Destination).filter(
            Destination.destination_id == visit_data.destination_id,
            Destination.is_active == True
        ).first()
        
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination {visit_data.destination_id} not found"
            )
        
        # Create visit log
        db_log = VisitLog(
            user_id=user_id,
            destination_id=visit_data.destination_id,
            visit_date=visit_data.visit_date,
            duration_minutes=visit_data.duration_minutes,
            completed=visit_data.completed
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        
        # Update destination stats
        RatingService._update_destination_stats(db, visit_data.destination_id)
        
        return db_log
    
    @staticmethod
    def get_user_visits(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[VisitLog]:
        """Get all visits by a user"""
        return db.query(VisitLog).filter(
            VisitLog.user_id == user_id
        ).order_by(desc(VisitLog.visit_date)).offset(skip).limit(limit).all()


class FeedbackService:
    """Service for tracking user feedback/interactions"""
    
    @staticmethod
    def create_feedback(db: Session, user_id: int, feedback_data: FeedbackCreate) -> UserFeedback:
        """Create a feedback entry"""
        # Check if destination exists
        destination = db.query(Destination).filter(
            Destination.destination_id == feedback_data.destination_id,
            Destination.is_active == True
        ).first()
        
        if not destination:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination {feedback_data.destination_id} not found"
            )
        
        # Create feedback
        db_feedback = UserFeedback(
            user_id=user_id,
            destination_id=feedback_data.destination_id,
            action=feedback_data.action,
            context=feedback_data.context
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        return db_feedback
    
    @staticmethod
    def get_user_feedback(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[UserFeedback]:
        """Get all feedback by a user"""
        return db.query(UserFeedback).filter(
            UserFeedback.user_id == user_id
        ).order_by(desc(UserFeedback.created_date)).offset(skip).limit(limit).all()

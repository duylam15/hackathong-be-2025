"""
Tour Recommendation Endpoints
"""

"""
Tour Recommendation Endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.services.tour_recommendation_service import TourRecommendationService
from app.schemas.tour import (
    TourRequest,
    TourRecommendation,
    ScoreAnalysis,
    UserProfile
)

router = APIRouter()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@router.post("/recommend", response_model=TourRecommendation)
def get_tour_recommendation(
    request: TourRequest,
    db: Session = Depends(get_db)
):
    """
    Tạo gợi ý tour dựa trên user profile
    """
    logger.debug("📩 Nhận request tạo tour gợi ý")

    # Convert StartLocation to dict
    start_loc_dict = None
    if request.start_location:
        start_loc_dict = {
            'id': 0,
            'name': request.start_location.name,
            'latitude': request.start_location.latitude,
            'longitude': request.start_location.longitude,
            'visit_time': 0,
            'price': 0
        }
        logger.debug(f"🏁 Start location: {start_loc_dict}")
    else:
        logger.debug("⚠️ Không có start_location trong request")

    # Convert UserProfile to dict
    user_dict = request.user_profile.model_dump()
    logger.debug(f"👤 User profile: {user_dict}")

    # Gọi service
    result = TourRecommendationService.get_tour_recommendations(
        db=db,
        user_profile=user_dict,
        start_location=start_loc_dict
    )
    logger.debug(f"🧠 Kết quả gợi ý: {result}")

    if not result['success']:
        logger.error(f"❌ Lỗi tạo tour: {result.get('message')}")
        raise HTTPException(status_code=400, detail=result.get('message', 'Không thể tạo tour'))

    logger.info("✅ Tạo tour gợi ý thành công")
    return result


@router.post("/analyze-scores", response_model=ScoreAnalysis)
def analyze_destination_scores(
    user_profile: UserProfile,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    """
    Phân tích điểm của các địa điểm cho user profile
    
    - **user_profile**: Thông tin người dùng
    - **top_n**: Số lượng địa điểm top muốn xem (default: 10)
    
    Returns:
    - Danh sách top destinations với điểm số
    """
    user_dict = user_profile.model_dump()
    
    result = TourRecommendationService.analyze_destination_scores(
        db=db,
        user_profile=user_dict,
        top_n=top_n
    )
    
    return result


@router.post("/quick-recommend")
def quick_recommend(
    user_type: str,
    budget: int,
    time_available: int,
    db: Session = Depends(get_db)
):
    """
    Gợi ý tour nhanh với thông tin tối thiểu
    
    - **user_type**: Loại user (Adventure, Cultural, Family, Relaxation, Budget)
    - **budget**: Ngân sách (VNĐ)
    - **time_available**: Thời gian có sẵn (giờ)
    """
    # Default preferences by type
    preference_map = {
        'Adventure': ['nature', 'hiking', 'adventure', 'outdoor'],
        'Cultural': ['culture', 'history', 'museum', 'architecture'],
        'Family': ['family', 'safe', 'entertainment', 'park'],
        'Relaxation': ['relaxation', 'spa', 'quiet', 'nature'],
        'Budget': ['budget', 'local', 'cheap', 'walking']
    }
    
    user_profile = {
        'type': user_type,
        'preference': preference_map.get(user_type, ['general']),
        'budget': budget,
        'time_available': time_available,
        'max_locations': 5
    }
    
    result = TourRecommendationService.get_tour_recommendations(
        db=db,
        user_profile=user_profile,
        start_location=None
    )
    
    if not result['success']:
        raise HTTPException(status_code=400, detail=result.get('message', 'Không thể tạo tour'))
    
    return result

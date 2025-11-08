"""
Schemas cho Tour Recommendation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class UserType(str, Enum):
    """Loại user profile"""
    ADVENTURE = "Adventure"
    CULTURAL = "Cultural"
    FAMILY = "Family"
    RELAXATION = "Relaxation"
    BUDGET = "Budget"


class UserProfile(BaseModel):
    """User profile cho tour recommendation"""
    name: Optional[str] = None
    type: UserType = Field(..., description="Loại user: Adventure, Cultural, Family, Relaxation, Budget")
    preference: List[str] = Field(
        ...,
        description="Danh sách sở thích: ['nature', 'hiking', 'culture', 'history', ...]"
    )
    budget: int = Field(..., description="Ngân sách (VNĐ)")
    time_available: int = Field(..., description="Thời gian có sẵn (giờ)")
    max_locations: int = Field(default=5, description="Số địa điểm tối đa muốn tham quan")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Nguyễn Văn A",
                "type": "Adventure",
                "preference": ["nature", "hiking", "adventure", "photography"],
                "budget": 1500000,
                "time_available": 8,
                "max_locations": 5
            }
        }


class StartLocation(BaseModel):
    """Điểm khởi hành"""
    name: str = Field(..., description="Tên điểm khởi hành")
    latitude: float = Field(..., description="Vĩ độ")
    longitude: float = Field(..., description="Kinh độ")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Khách sạn Quận 1",
                "latitude": 10.7769,
                "longitude": 106.7009
            }
        }


class TourRequest(BaseModel):
    """Request để tạo tour recommendation"""
    user_profile: UserProfile
    start_location: Optional[StartLocation] = None


class RouteLocation(BaseModel):
    """Một địa điểm trong lộ trình"""
    id: int
    name: str
    type: str
    latitude: float
    longitude: float
    location_address: Optional[str] = None
    price: int
    visit_time: int
    travel_time: int
    score: float
    opening_hours: Optional[str] = None
    facilities: List[str] = []
    images: List[str] = []  # Danh sách URLs hình ảnh của địa điểm


class TourRecommendation(BaseModel):
    """Kết quả tour recommendation"""
    success: bool
    route: List[RouteLocation] = []
    total_locations: int = 0
    total_time: int = 0
    total_distance: float = 0.0
    total_score: float = 0.0
    total_cost: int = 0
    avg_score: float = 0.0
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "route": [
                    {
                        "id": 7,
                        "name": "Bitexco Financial Tower",
                        "type": "Adventure",
                        "latitude": 10.7715,
                        "longitude": 106.7038,
                        "location_address": "36 Hồ Tùng Mậu, Bến Nghé, Quận 1, TP.HCM",
                        "price": 200000,
                        "visit_time": 90,
                        "travel_time": 5,
                        "score": 0.85,
                        "opening_hours": "09:30-21:30",
                        "facilities": ["parking", "restroom", "restaurant"]
                    }
                ],
                "total_locations": 5,
                "total_time": 420,
                "total_distance": 15.5,
                "total_score": 4.2,
                "total_cost": 500000,
                "avg_score": 0.84
            }
        }


class DestinationScore(BaseModel):
    """Điểm của một địa điểm"""
    id: int
    name: str
    type: str
    tags: List[str]
    price: int
    score: float


class ScoreAnalysis(BaseModel):
    """Phân tích điểm của destinations"""
    success: bool
    user_profile: Dict[str, Any]
    top_destinations: List[DestinationScore]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "user_profile": {
                    "type": "Adventure",
                    "preference": ["nature", "hiking"],
                    "budget": 1000000,
                    "time_available": 8
                },
                "top_destinations": [
                    {
                        "id": 7,
                        "name": "Bitexco Financial Tower",
                        "type": "Adventure",
                        "tags": ["city", "view", "skyscraper"],
                        "price": 200000,
                        "score": 0.85
                    }
                ]
            }
        }

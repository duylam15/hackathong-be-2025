from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class DestinationBase(BaseModel):
    """Base Destination schema theo destinations_data.json"""
    destination_name: str
    destination_type: Optional[str] = None  # Cultural, Budget, Relaxation, Adventure
    tags: List[str] = []  # ["history", "culture", "architecture", ...]
    location_address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    price: int = 0  # Giá vé (VNĐ)
    opening_hours: Optional[str] = None  # "08:00-17:00"
    visit_time: Optional[int] = None  # Thời gian tham quan (phút)
    facilities: List[str] = []  # ["parking", "restroom", "wifi", ...]
    extra_info: Dict[str, Any] = {}  # {"rating": 4.6, "reviews": 8500} - renamed from 'metadata'


class DestinationCreate(DestinationBase):
    """Schema for creating a destination"""
    pass


class DestinationUpdate(BaseModel):
    """Schema for updating a destination"""
    destination_name: Optional[str] = None
    destination_type: Optional[str] = None
    tags: Optional[List[str]] = None
    location_address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    price: Optional[int] = None
    opening_hours: Optional[str] = None
    visit_time: Optional[int] = None
    facilities: Optional[List[str]] = None
    extra_info: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DestinationInDB(DestinationBase):
    """Schema for destination in database"""
    destination_id: int
    created_date: datetime
    updated_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class DestinationResponse(DestinationInDB):
    """Schema for destination response"""
    pass


# Category schemas
class CategoryBase(BaseModel):
    """Base Category schema"""
    category_name: str
    category_description: Optional[str] = None
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryInDB(CategoryBase):
    """Schema for category in database"""
    category_id: int
    
    class Config:
        from_attributes = True


class CategoryResponse(CategoryInDB):
    """Schema for category response"""
    pass


# Destination Description schemas
class DescriptionBase(BaseModel):
    """Base Description schema"""
    language_code: str = "en"
    title: Optional[str] = None
    short_description: Optional[str] = None
    full_description: Optional[str] = None
    history_info: Optional[str] = None
    cultural_info: Optional[str] = None
    travel_tips: Optional[str] = None


class DescriptionCreate(DescriptionBase):
    """Schema for creating a description"""
    destination_id: int


class DescriptionInDB(DescriptionBase):
    """Schema for description in database"""
    description_id: int
    destination_id: int
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True


class DescriptionResponse(DescriptionInDB):
    """Schema for description response"""
    pass

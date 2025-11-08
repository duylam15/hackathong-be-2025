from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class DestinationBase(BaseModel):
    """Base Destination schema"""
    destination_name: str
    location_address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    destination_type: Optional[str] = None
    popularity_score: int = 0
    avg_duration: Optional[int] = None


class DestinationCreate(DestinationBase):
    """Schema for creating a destination"""
    company_id: Optional[int] = None


class DestinationUpdate(BaseModel):
    """Schema for updating a destination"""
    destination_name: Optional[str] = None
    location_address: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    destination_type: Optional[str] = None
    popularity_score: Optional[int] = None
    avg_duration: Optional[int] = None
    is_active: Optional[bool] = None


class DestinationInDB(DestinationBase):
    """Schema for destination in database"""
    destination_id: int
    company_id: Optional[int]
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

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TagBase(BaseModel):
    """Base Tag schema"""
    tag_name: str = Field(..., description="Tên tag (lowercase, no spaces): history, culture, nature")
    tag_display_name: str = Field(..., description="Tên hiển thị: Lịch sử, Văn hóa, Thiên nhiên")
    tag_category: str = Field(..., description="Loại tag: interest, activity, atmosphere")
    description: Optional[str] = Field(None, description="Mô tả chi tiết về tag")
    icon: Optional[str] = Field(None, description="Icon/emoji: 🏛️, 🎨, 🌿")


class TagCreate(TagBase):
    """Schema for creating a tag"""
    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag - all fields optional"""
    tag_name: Optional[str] = None
    tag_display_name: Optional[str] = None
    tag_category: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


class TagResponse(TagBase):
    """Schema for tag response"""
    tag_id: int
    created_date: datetime
    updated_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Schema for tag list response with categories"""
    tags: List[TagResponse]
    total: int
    categories: List[str]  # List of unique categories
    
    class Config:
        from_attributes = True

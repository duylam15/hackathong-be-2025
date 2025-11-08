from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime


class UserBase(BaseModel):
    """Base User schema"""
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    profile_image: Optional[str] = None
    status: Optional[str] = None


class UserInDB(UserBase):
    """Schema for user in database"""
    id: int
    registration_date: datetime
    status: str
    
    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """Schema for user response"""
    pass

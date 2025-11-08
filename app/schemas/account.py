from pydantic import BaseModel, Field
from typing import Optional


class AccountBase(BaseModel):
    """Base Account schema"""
    usename: str = Field(..., description="Username")
    role: str = "user"


class AccountCreate(AccountBase):
    """Schema for creating an account"""
    user_id: int
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")


class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[str] = None
    status: Optional[str] = None


class AccountLogin(BaseModel):
    """Schema for login"""
    usename: str
    password: str


class AccountInDB(AccountBase):
    """Schema for account in database"""
    id: int
    user_id: int
    status: str
    
    class Config:
        from_attributes = True


class AccountResponse(AccountInDB):
    """Schema for account response"""
    pass


class Token(BaseModel):
    """Schema for JWT token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data"""
    account_id: Optional[int] = None
    username: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Schema for changing password"""
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Schema for registration"""
    # User info
    full_name: str
    email: str
    phone: Optional[str] = None
    # Account info
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    role: str = "user"

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db.database import get_db
from app.core.config import settings
from app.core.security import decode_access_token
from app.models.account import Account
from app.models.user import User

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Dependency to get database session
def get_database() -> Generator:
    """Get database session"""
    try:
        db = next(get_db())
        yield db
    finally:
        pass


def get_current_account(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_database)
) -> Account:
    """Get current authenticated account from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    account = db.query(Account).filter(Account.usename == username).first()
    if account is None:
        raise credentials_exception
    
    if account.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    
    return account


def get_current_user(
    account: Account = Depends(get_current_account),
    db: Session = Depends(get_database)
) -> User:
    """Get current authenticated user"""
    user = db.query(User).filter(User.id == account.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    return user


def require_role(required_role: str):
    """Dependency to check if user has required role"""
    def role_checker(account: Account = Depends(get_current_account)) -> Account:
        if account.role != required_role and account.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return account
    return role_checker


# Shorthand for admin only
def get_current_admin(account: Account = Depends(get_current_account)) -> Account:
    """Get current admin account"""
    if account.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return account

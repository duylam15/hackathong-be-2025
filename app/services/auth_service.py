from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountLogin, Token
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.core.config import settings


class AuthService:
    """Service layer for Authentication operations"""
    
    @staticmethod
    def register(db: Session, user_data: UserCreate, account_data: AccountCreate) -> dict:
        """Register a new user with account"""
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        existing_account = db.query(Account).filter(Account.usename == account_data.usename).first()
        if existing_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        db_user = User(**user_data.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create account with hashed password
        hashed_password = get_password_hash(account_data.password)
        db_account = Account(
            user_id=db_user.id,
            usename=account_data.usename,
            password=hashed_password,
            role=account_data.role,
            status="active"
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Generate token
        access_token = create_access_token(
            data={
                "sub": db_account.usename,
                "user_id": db_user.id,
                "account_id": db_account.id,
                "role": db_account.role
            }
        )
        
        return {
            "user": db_user,
            "account": db_account,
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def login(db: Session, login_data: AccountLogin) -> Token:
        """Login user and return JWT token"""
        # Find account by username
        account = db.query(Account).filter(Account.usename == login_data.usename).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(login_data.password, account.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check account status
        if account.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is not active"
            )
        
        # Get user info
        user = db.query(User).filter(User.id == account.user_id).first()
        if not user or user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is not active"
            )
        
        # Generate token
        access_token = create_access_token(
            data={
                "sub": account.usename,
                "user_id": user.id,
                "account_id": account.id,
                "role": account.role
            }
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    @staticmethod
    def get_current_user(db: Session, username: str) -> Optional[dict]:
        """Get current user by username from token"""
        account = db.query(Account).filter(Account.usename == username).first()
        if not account:
            return None
        
        user = db.query(User).filter(User.id == account.user_id).first()
        if not user:
            return None
        
        return {
            "user": user,
            "account": account
        }
    
    @staticmethod
    def change_password(
        db: Session,
        account_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """Change user password"""
        account = db.query(Account).filter(Account.id == account_id).first()
        
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Verify old password
        if not verify_password(old_password, account.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect"
            )
        
        # Update password
        account.password = get_password_hash(new_password)
        db.commit()
        
        return True

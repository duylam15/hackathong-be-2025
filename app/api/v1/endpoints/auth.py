from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_database, get_current_account, get_current_user
from app.schemas.account import (
    Token, AccountLogin, RegisterRequest, 
    ChangePasswordRequest, AccountResponse
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.account import Account
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_database)
):
    """Register a new user account"""
    from app.schemas.user import UserCreate
    from app.schemas.account import AccountCreate
    
    # Split data for user and account
    user_data = UserCreate(
        full_name=register_data.full_name,
        email=register_data.email,
        phone=register_data.phone
    )
    
    account_data = AccountCreate(
        user_id=0,  # Will be set in service
        usename=register_data.username,
        password=register_data.password,
        role=register_data.role
    )
    
    result = AuthService.register(db, user_data, account_data)
    
    return {
        "message": "User registered successfully",
        "user": {
            "id": result["user"].id,
            "full_name": result["user"].full_name,
            "email": result["user"].email
        },
        "account": {
            "id": result["account"].id,
            "username": result["account"].usename,
            "role": result["account"].role
        },
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database)
):
    """Login with username and password (OAuth2 compatible)"""
    login_data = AccountLogin(
        usename=form_data.username,
        password=form_data.password
    )
    return AuthService.login(db, login_data)


@router.post("/login/json", response_model=Token)
def login_json(
    login_data: AccountLogin,
    db: Session = Depends(get_database)
):
    """Login with JSON body"""
    return AuthService.login(db, login_data)


@router.get("/me", response_model=dict)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    current_account: Account = Depends(get_current_account)
):
    """Get current authenticated user information"""
    return {
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "phone": current_user.phone,
            "status": current_user.status
        },
        "account": {
            "id": current_account.id,
            "username": current_account.usename,
            "role": current_account.role,
            "status": current_account.status
        }
    }


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    current_account: Account = Depends(get_current_account),
    db: Session = Depends(get_database)
):
    """Change current user password"""
    success = AuthService.change_password(
        db,
        current_account.id,
        password_data.old_password,
        password_data.new_password
    )
    
    return {
        "message": "Password changed successfully"
    }


@router.post("/logout")
def logout(current_account: Account = Depends(get_current_account)):
    """Logout user (client should delete token)"""
    return {
        "message": "Logged out successfully. Please delete your access token."
    }

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_database
from app.schemas.tag import (
    TagCreate,
    TagUpdate,
    TagResponse,
    TagListResponse
)
from app.services.tag_service import TagService

router = APIRouter()


@router.get("/", response_model=TagListResponse)
def get_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    category: Optional[str] = Query(None, description="Filter by category: interest, activity, atmosphere"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: Session = Depends(get_database)
):
    """
    Get list of tags for user to choose
    
    Returns tags grouped by categories:
    - **interest**: Sở thích (history, culture, nature, art, food...)
    - **activity**: Hoạt động (hiking, shopping, photography...)
    - **atmosphere**: Không khí (relaxation, adventure, family...)
    
    FE có thể dùng endpoint này để:
    1. Lấy tất cả tags: không truyền category
    2. Lấy theo category: truyền category=interest
    3. Group by category: dùng field `categories` trong response
    """
    tags = TagService.get_tags(db, skip=skip, limit=limit, category=category, is_active=is_active)
    categories = TagService.get_categories(db)
    
    return TagListResponse(
        tags=tags,
        total=len(tags),
        categories=categories
    )


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_database)
):
    """Get tag by ID"""
    tag = TagService.get_tag_by_id(db, tag_id=tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    return tag


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_database)
):
    """
    Create a new tag
    
    Required fields:
    - **tag_name**: Tên tag (lowercase, no spaces)
    - **tag_display_name**: Tên hiển thị tiếng Việt
    - **tag_category**: Loại tag (interest, activity, atmosphere)
    
    Optional:
    - **description**: Mô tả chi tiết
    - **icon**: Icon/emoji
    """
    # Check if tag_name already exists
    existing = TagService.get_tag_by_name(db, tag_name=tag_data.tag_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_data.tag_name}' already exists"
        )
    
    try:
        tag = TagService.create_tag(db, tag_data=tag_data)
        return tag
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create tag: {str(e)}"
        )


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_database)
):
    """Update an existing tag"""
    tag = TagService.update_tag(db, tag_id=tag_id, tag_data=tag_data)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_database)
):
    """Delete a tag (soft delete)"""
    success = TagService.delete_tag(db, tag_id=tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    return None

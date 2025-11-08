from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate


class TagService:
    """Service for Tag operations"""
    
    @staticmethod
    def get_tags(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> List[Tag]:
        """Get list of tags with optional filters"""
        query = db.query(Tag)
        
        if is_active is not None:
            query = query.filter(Tag.is_active == is_active)
        
        if category:
            query = query.filter(Tag.tag_category == category)
        
        return query.order_by(Tag.tag_category, Tag.tag_name).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_tag_by_id(db: Session, tag_id: int) -> Optional[Tag]:
        """Get a tag by ID"""
        return db.query(Tag).filter(Tag.tag_id == tag_id).first()
    
    @staticmethod
    def get_tag_by_name(db: Session, tag_name: str) -> Optional[Tag]:
        """Get a tag by name"""
        return db.query(Tag).filter(Tag.tag_name == tag_name).first()
    
    @staticmethod
    def create_tag(db: Session, tag_data: TagCreate) -> Tag:
        """Create a new tag"""
        tag = Tag(**tag_data.model_dump())
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag
    
    @staticmethod
    def update_tag(db: Session, tag_id: int, tag_data: TagUpdate) -> Optional[Tag]:
        """Update an existing tag"""
        tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
        if not tag:
            return None
        
        update_data = tag_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)
        
        db.commit()
        db.refresh(tag)
        return tag
    
    @staticmethod
    def delete_tag(db: Session, tag_id: int) -> bool:
        """Delete a tag (soft delete)"""
        tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
        if not tag:
            return False
        
        tag.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_categories(db: Session) -> List[str]:
        """Get all unique tag categories"""
        result = db.query(Tag.tag_category).filter(Tag.is_active == True).distinct().all()
        return [r[0] for r in result]

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.database import Base


class Tag(Base):
    """
    Model Tag - Lưu các tag/sở thích để người dùng chọn
    Tags này dùng cho tour recommendation
    """
    __tablename__ = "tag"
    
    tag_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tag_name = Column(String, nullable=False, unique=True, index=True)  # "history", "culture", "nature"
    tag_display_name = Column(String, nullable=False)  # "Lịch sử", "Văn hóa", "Thiên nhiên"
    tag_category = Column(String, nullable=False)  # "interest", "activity", "atmosphere"
    description = Column(String)  # Mô tả chi tiết về tag
    icon = Column(String)  # Icon/emoji để hiển thị: "🏛️", "🎨", "🌿"
    
    # Audit fields
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Tag(id={self.tag_id}, name={self.tag_name}, display={self.tag_display_name})>"

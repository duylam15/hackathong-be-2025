"""
Migration script to create tags table and seed initial tags data
"""
from app.db.database import engine
from app.models import Base, Tag
from app.db.database import SessionLocal
from sqlalchemy import text


def create_tags_table():
    """Create tags table"""
    print("Creating tags table...")
    Base.metadata.create_all(bind=engine, tables=[Tag.__table__])
    print("✅ Tags table created successfully")


def seed_tags_data():
    """Seed initial tags data"""
    db = SessionLocal()
    
    try:
        print("\nSeeding tags data...")
        
        # Comprehensive list of tags for tour recommendation
        tags_data = [
            # ===== INTEREST (Sở thích) =====
            {
                "tag_name": "history",
                "tag_display_name": "Lịch sử",
                "tag_category": "interest",
                "description": "Địa điểm lịch sử, di tích văn hóa",
                "icon": "🏛️"
            },
            {
                "tag_name": "culture",
                "tag_display_name": "Văn hóa",
                "tag_category": "interest",
                "description": "Văn hóa truyền thống, phong tục tập quán",
                "icon": "🎭"
            },
            {
                "tag_name": "architecture",
                "tag_display_name": "Kiến trúc",
                "tag_category": "interest",
                "description": "Công trình kiến trúc đẹp",
                "icon": "🏗️"
            },
            {
                "tag_name": "art",
                "tag_display_name": "Nghệ thuật",
                "tag_category": "interest",
                "description": "Bảo tàng nghệ thuật, triển lãm",
                "icon": "🎨"
            },
            {
                "tag_name": "museum",
                "tag_display_name": "Bảo tàng",
                "tag_category": "interest",
                "description": "Bảo tàng các loại",
                "icon": "🏛️"
            },
            {
                "tag_name": "nature",
                "tag_display_name": "Thiên nhiên",
                "tag_category": "interest",
                "description": "Cảnh quan thiên nhiên, vườn quốc gia",
                "icon": "🌿"
            },
            {
                "tag_name": "food",
                "tag_display_name": "Ẩm thực",
                "tag_category": "interest",
                "description": "Món ăn địa phương, nhà hàng",
                "icon": "🍜"
            },
            {
                "tag_name": "street_food",
                "tag_display_name": "Ẩm thực đường phố",
                "tag_category": "interest",
                "description": "Món ăn vỉa hè, chợ ăn uống",
                "icon": "🥘"
            },
            {
                "tag_name": "local",
                "tag_display_name": "Địa phương",
                "tag_category": "interest",
                "description": "Trải nghiệm địa phương, dân dã",
                "icon": "🏘️"
            },
            {
                "tag_name": "religion",
                "tag_display_name": "Tôn giáo",
                "tag_category": "interest",
                "description": "Chùa chiền, nhà thờ",
                "icon": "⛪"
            },
            {
                "tag_name": "education",
                "tag_display_name": "Giáo dục",
                "tag_category": "interest",
                "description": "Học tập, tìm hiểu kiến thức",
                "icon": "📚"
            },
            {
                "tag_name": "landmark",
                "tag_display_name": "Địa danh",
                "tag_category": "interest",
                "description": "Địa điểm nổi tiếng, biểu tượng",
                "icon": "📍"
            },
            
            # ===== ACTIVITY (Hoạt động) =====
            {
                "tag_name": "photography",
                "tag_display_name": "Chụp ảnh",
                "tag_category": "activity",
                "description": "Địa điểm đẹp để chụp ảnh",
                "icon": "📷"
            },
            {
                "tag_name": "shopping",
                "tag_display_name": "Mua sắm",
                "tag_category": "activity",
                "description": "Chợ, trung tâm thương mại",
                "icon": "🛍️"
            },
            {
                "tag_name": "hiking",
                "tag_display_name": "Leo núi",
                "tag_category": "activity",
                "description": "Đi bộ đường dài, leo núi",
                "icon": "🥾"
            },
            {
                "tag_name": "outdoor",
                "tag_display_name": "Ngoài trời",
                "tag_category": "activity",
                "description": "Hoạt động ngoài trời",
                "icon": "🏕️"
            },
            {
                "tag_name": "sports",
                "tag_display_name": "Thể thao",
                "tag_category": "activity",
                "description": "Hoạt động thể thao",
                "icon": "⚽"
            },
            {
                "tag_name": "water_activities",
                "tag_display_name": "Hoạt động nước",
                "tag_category": "activity",
                "description": "Bơi lội, lặn biển",
                "icon": "🏊"
            },
            {
                "tag_name": "entertainment",
                "tag_display_name": "Giải trí",
                "tag_category": "activity",
                "description": "Vui chơi giải trí",
                "icon": "🎪"
            },
            {
                "tag_name": "nightlife",
                "tag_display_name": "Cuộc sống đêm",
                "tag_category": "activity",
                "description": "Bar, club, phố đêm",
                "icon": "🌃"
            },
            {
                "tag_name": "sightseeing",
                "tag_display_name": "Tham quan",
                "tag_category": "activity",
                "description": "Ngắm cảnh, tham quan",
                "icon": "👀"
            },
            {
                "tag_name": "walking",
                "tag_display_name": "Đi bộ",
                "tag_category": "activity",
                "description": "Dạo bộ, khám phá đi bộ",
                "icon": "🚶"
            },
            
            # ===== ATMOSPHERE (Không khí) =====
            {
                "tag_name": "relaxation",
                "tag_display_name": "Thư giãn",
                "tag_category": "atmosphere",
                "description": "Yên tĩnh, thư giãn",
                "icon": "🧘"
            },
            {
                "tag_name": "adventure",
                "tag_display_name": "Phiêu lưu",
                "tag_category": "atmosphere",
                "description": "Mạo hiểm, khám phá",
                "icon": "🧗"
            },
            {
                "tag_name": "family",
                "tag_display_name": "Gia đình",
                "tag_category": "atmosphere",
                "description": "Phù hợp cho gia đình, trẻ em",
                "icon": "👨‍👩‍👧‍👦"
            },
            {
                "tag_name": "romantic",
                "tag_display_name": "Lãng mạn",
                "tag_category": "atmosphere",
                "description": "Phù hợp cho cặp đôi",
                "icon": "💑"
            },
            {
                "tag_name": "peaceful",
                "tag_display_name": "Yên bình",
                "tag_category": "atmosphere",
                "description": "Không gian yên tĩnh, thanh bình",
                "icon": "☮️"
            },
            {
                "tag_name": "vibrant",
                "tag_display_name": "Sôi động",
                "tag_category": "atmosphere",
                "description": "Nhộn nhịp, sôi động",
                "icon": "🎉"
            },
            {
                "tag_name": "luxury",
                "tag_display_name": "Sang trọng",
                "tag_category": "atmosphere",
                "description": "Cao cấp, xa hoa",
                "icon": "💎"
            },
            {
                "tag_name": "budget",
                "tag_display_name": "Tiết kiệm",
                "tag_category": "atmosphere",
                "description": "Giá cả phải chăng",
                "icon": "💰"
            },
            {
                "tag_name": "authentic",
                "tag_display_name": "Chân thật",
                "tag_category": "atmosphere",
                "description": "Trải nghiệm chân thật, địa phương",
                "icon": "✨"
            },
            {
                "tag_name": "modern",
                "tag_display_name": "Hiện đại",
                "tag_category": "atmosphere",
                "description": "Hiện đại, công nghệ cao",
                "icon": "🏙️"
            }
        ]
        
        # Check and create tags
        created_count = 0
        for tag_data in tags_data:
            # Check if tag already exists
            existing = db.query(Tag).filter(Tag.tag_name == tag_data["tag_name"]).first()
            if existing:
                print(f"  ⏭️  Tag '{tag_data['tag_name']}' already exists, skipping...")
                continue
            
            tag = Tag(**tag_data)
            db.add(tag)
            created_count += 1
            print(f"  ✓ Created tag: {tag_data['tag_display_name']} ({tag_data['tag_name']})")
        
        db.commit()
        print(f"\n✅ Successfully seeded {created_count} tags!")
        print(f"   Total tags in database: {db.query(Tag).count()}")
        
        # Show summary by category
        print("\n📊 Tags summary by category:")
        for category in ["interest", "activity", "atmosphere"]:
            count = db.query(Tag).filter(Tag.tag_category == category).count()
            print(f"   - {category.title()}: {count} tags")
        
    except Exception as e:
        print(f"\n❌ Error seeding tags: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Tags Migration Script")
    print("=" * 70)
    
    create_tags_table()
    seed_tags_data()
    
    print("\n" + "=" * 70)
    print("✅ Migration completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart your FastAPI server")
    print("2. Access API docs: http://localhost:8000/docs")
    print("3. Test endpoint: GET /api/v1/tags/")
    print("=" * 70)

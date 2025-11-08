"""
Script để migrate database schema cho Destination model
Chạy script này để cập nhật database với các columns mới
"""

import sys
from sqlalchemy import text
from app.db.database import SessionLocal

def migrate_destination_schema():
    """Migrate destination table schema"""
    
    db = SessionLocal()
    
    try:
        print("🔄 Bắt đầu migration...")
        
        # Check if columns exist
        check_columns = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'destination'
        """)
        
        result = db.execute(check_columns)
        existing_columns = [row[0] for row in result]
        
        print(f"📋 Columns hiện tại: {existing_columns}")
        
        migrations = []
        
        # 1. Add tags column if not exists
        if 'tags' not in existing_columns:
            migrations.append("""
                ALTER TABLE destination 
                ADD COLUMN tags TEXT[] DEFAULT ARRAY[]::TEXT[]
            """)
            print("  ✓ Sẽ thêm column: tags")
        
        # 2. Add facilities column if not exists
        if 'facilities' not in existing_columns:
            migrations.append("""
                ALTER TABLE destination 
                ADD COLUMN facilities TEXT[] DEFAULT ARRAY[]::TEXT[]
            """)
            print("  ✓ Sẽ thêm column: facilities")
        
        # 3. Add extra_info column if not exists
        if 'extra_info' not in existing_columns:
            migrations.append("""
                ALTER TABLE destination 
                ADD COLUMN extra_info JSONB DEFAULT '{}'::JSONB
            """)
            print("  ✓ Sẽ thêm column: extra_info")
        
        # 4. Add opening_hours column if not exists
        if 'opening_hours' not in existing_columns:
            migrations.append("""
                ALTER TABLE destination 
                ADD COLUMN opening_hours VARCHAR
            """)
            print("  ✓ Sẽ thêm column: opening_hours")
        
        # 5. Add visit_time column if not exists
        if 'visit_time' not in existing_columns:
            migrations.append("""
                ALTER TABLE destination 
                ADD COLUMN visit_time INTEGER
            """)
            print("  ✓ Sẽ thêm column: visit_time")
        
        # 6. Add price column if not exists
        if 'price' not in existing_columns:
            migrations.append("""
                ALTER TABLE destination 
                ADD COLUMN price INTEGER DEFAULT 0
            """)
            print("  ✓ Sẽ thêm column: price")
        
        # 7. Drop company_id if exists (no longer needed)
        if 'company_id' in existing_columns:
            # First drop foreign key constraint if exists
            migrations.append("""
                ALTER TABLE destination 
                DROP CONSTRAINT IF EXISTS destination_company_id_fkey
            """)
            migrations.append("""
                ALTER TABLE destination 
                DROP COLUMN IF EXISTS company_id
            """)
            print("  ✓ Sẽ xóa column: company_id")
        
        # 8. Drop old columns if exist
        old_columns = ['popularity_score', 'avg_duration']
        for col in old_columns:
            if col in existing_columns:
                migrations.append(f"""
                    ALTER TABLE destination 
                    DROP COLUMN IF EXISTS {col}
                """)
                print(f"  ✓ Sẽ xóa column: {col}")
        
        if not migrations:
            print("\n✅ Database đã cập nhật, không cần migration!")
            return
        
        # Execute migrations
        print(f"\n🔧 Thực thi {len(migrations)} migrations...")
        
        for i, migration_sql in enumerate(migrations, 1):
            try:
                db.execute(text(migration_sql))
                print(f"  ✓ Migration {i}/{len(migrations)} thành công")
            except Exception as e:
                print(f"  ⚠️  Migration {i}/{len(migrations)} warning: {str(e)}")
                # Continue with other migrations
        
        db.commit()
        print("\n✅ Migration hoàn thành!")
        
        # Show final schema
        result = db.execute(check_columns)
        final_columns = [row[0] for row in result]
        print(f"\n📋 Columns sau migration: {final_columns}")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {str(e)}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


def check_destination_table():
    """Kiểm tra bảng destination có tồn tại không"""
    db = SessionLocal()
    
    try:
        check_table = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'destination'
            )
        """)
        
        result = db.execute(check_table)
        exists = result.scalar()
        
        if not exists:
            print("❌ Bảng 'destination' không tồn tại!")
            print("💡 Bạn cần chạy: alembic upgrade head")
            sys.exit(1)
        
        print("✓ Bảng 'destination' đã tồn tại")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("="*70)
    print("🗄️  MIGRATION DESTINATION SCHEMA")
    print("="*70)
    print()
    
    # Check if table exists
    check_destination_table()
    
    # Run migration
    migrate_destination_schema()
    
    print("\n" + "="*70)
    print("✅ Hoàn tất! Bạn có thể restart server và test API.")
    print("="*70)

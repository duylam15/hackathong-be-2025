"""
Migration script to add images column to destination table
"""
from app.db.database import engine
from sqlalchemy import text

def add_images_column():
    """Add images column to destination table"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='destination' AND column_name='images'
            """))
            
            if result.fetchone():
                print("✓ Column 'images' already exists in destination table")
                return
            
            # Add the column
            conn.execute(text("""
                ALTER TABLE destination 
                ADD COLUMN images VARCHAR[] DEFAULT ARRAY[]::VARCHAR[]
            """))
            conn.commit()
            print("✅ Successfully added 'images' column to destination table")
            
    except Exception as e:
        print(f"❌ Error adding images column: {e}")
        raise

if __name__ == "__main__":
    print("=" * 60)
    print("Adding images column to destination table")
    print("=" * 60)
    add_images_column()
    print("=" * 60)
    print("Done!")
    print("=" * 60)

"""
Script to add sample images to existing destinations
"""
from app.db.database import engine
from sqlalchemy import text
import json

# Sample images for different destination types
SAMPLE_IMAGES = {
    "Nhà Thờ Đức Bà": [
        "https://images.unsplash.com/photo-1583417319070-4a69db38a482",
        "https://images.unsplash.com/photo-1589811213115-7e4b51d3b40a",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Saigon_Notre-Dame_Basilica.jpg/1200px-Saigon_Notre-Dame_Basilica.jpg"
    ],
    "Bến Nhà Rồng": [
        "https://images.unsplash.com/photo-1555993539-1732b0258235",
        "https://images.unsplash.com/photo-1528127269322-539801943592"
    ],
    "Phố Đi Bộ Nguyễn Huệ": [
        "https://images.unsplash.com/photo-1583417319070-4a69db38a482",
        "https://images.unsplash.com/photo-1542326319-00f0ba9be267",
        "https://picsum.photos/800/600?random=1"
    ],
    "default": [
        "https://picsum.photos/800/600?random=2",
        "https://picsum.photos/800/600?random=3"
    ]
}

def update_destination_images():
    """Update existing destinations with sample images"""
    try:
        with engine.connect() as conn:
            # Get all destinations
            result = conn.execute(text("SELECT destination_id, destination_name FROM destination"))
            destinations = result.fetchall()
            
            updated_count = 0
            for dest_id, dest_name in destinations:
                # Get appropriate images
                images = SAMPLE_IMAGES.get(dest_name, SAMPLE_IMAGES["default"])
                
                # Build array literal for PostgreSQL
                # Format: ARRAY['url1', 'url2', 'url3']
                array_values = ', '.join(f"'{img}'" for img in images)
                
                # Update destination with images - use string formatting to avoid parameter binding issues
                query = f"""
                    UPDATE destination 
                    SET images = ARRAY[{array_values}]::VARCHAR[]
                    WHERE destination_id = {dest_id}
                """
                conn.execute(text(query))
                updated_count += 1
                print(f"✓ Updated '{dest_name}' (ID: {dest_id}) with {len(images)} images")
            
            conn.commit()
            print(f"\n✅ Successfully updated {updated_count} destinations with sample images")
            
    except Exception as e:
        print(f"❌ Error updating images: {e}")
        raise

if __name__ == "__main__":
    print("=" * 70)
    print("Adding sample images to existing destinations")
    print("=" * 70)
    update_destination_images()
    print("=" * 70)
    print("Done! You can now test the API to see images in responses")
    print("=" * 70)

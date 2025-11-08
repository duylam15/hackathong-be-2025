"""
Script để import dữ liệu từ destinations_data.json vào database
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.services.destination_service import DestinationService


def import_destinations_from_json(json_file: str = "destinations_data.json"):
    """Import destinations từ JSON file vào database"""
    
    print(f"🔄 Đang đọc file {json_file}...")
    
    # Read JSON file
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            destinations_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file {json_file}")
        return
    except json.JSONDecodeError:
        print(f"❌ File {json_file} không phải JSON hợp lệ")
        return
    
    print(f"✅ Đọc thành công {len(destinations_data)} địa điểm")
    
    # Create database session
    db = SessionLocal()
    
    try:
        print("🔄 Đang import vào database...")
        
        # Bulk create
        created = DestinationService.bulk_create_from_json(db, destinations_data)
        
        print(f"✅ Import thành công {len(created)} địa điểm!")
        
        # Print summary
        print("\n📊 Tóm tắt:")
        type_counts = {}
        for dest in created:
            dest_type = dest.destination_type or "Unknown"
            type_counts[dest_type] = type_counts.get(dest_type, 0) + 1
        
        for dest_type, count in type_counts.items():
            print(f"  • {dest_type}: {count} địa điểm")
        
    except Exception as e:
        print(f"❌ Lỗi khi import: {str(e)}")
        db.rollback()
    finally:
        db.close()


def clear_all_destinations():
    """Xóa tất cả destinations (để re-import)"""
    db = SessionLocal()
    
    try:
        from app.models.destination import Destination
        
        count = db.query(Destination).count()
        
        if count == 0:
            print("ℹ️  Database đã trống")
            return
        
        confirm = input(f"⚠️  Bạn có chắc muốn xóa {count} destinations? (yes/no): ")
        
        if confirm.lower() == 'yes':
            db.query(Destination).delete()
            db.commit()
            print(f"✅ Đã xóa {count} destinations")
        else:
            print("❌ Hủy bỏ")
    
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--clear":
            clear_all_destinations()
        elif sys.argv[1] == "--help":
            print("""
Usage:
  python import_destinations.py              # Import từ destinations_data.json
  python import_destinations.py <file.json>  # Import từ file khác
  python import_destinations.py --clear      # Xóa tất cả destinations
  python import_destinations.py --help       # Hiện help
            """)
        else:
            import_destinations_from_json(sys.argv[1])
    else:
        import_destinations_from_json()

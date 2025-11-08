"""
Test Tour Recommendation với Fallback Mechanism
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.tour_recommendation_service import TourRecommendationService

def test_tour_recommendation():
    """Test với request thực tế"""
    
    print("=" * 80)
    print("🧪 TEST TOUR RECOMMENDATION WITH FALLBACK")
    print("=" * 80)
    
    # User profile từ request
    user_profile = {
        "name": "Nguyễn Văn A",
        "type": "Adventure",
        "preference": ["nature", "hiking", "adventure"],
        "budget": 1500000,
        "time_available": 8,
        "max_locations": 8
    }
    
    start_location = {
        "name": "Khách sạn Quận 1",
        "latitude": 10.7769,
        "longitude": 106.7009
    }
    
    print(f"\n👤 User Profile:")
    print(f"   - Type: {user_profile['type']}")
    print(f"   - Preferences: {', '.join(user_profile['preference'])}")
    print(f"   - Budget: {user_profile['budget']:,} VNĐ")
    print(f"   - Time: {user_profile['time_available']} giờ")
    print(f"   - Max locations: {user_profile['max_locations']}")
    
    print(f"\n🏁 Start Location:")
    print(f"   - {start_location['name']}")
    print(f"   - ({start_location['latitude']}, {start_location['longitude']})")
    
    # Connect to database
    db = SessionLocal()
    
    try:
        print(f"\n🚀 Calling TourRecommendationService...")
        print("-" * 80)
        
        result = TourRecommendationService.get_tour_recommendations(
            db=db,
            user_profile=user_profile,
            start_location=start_location
        )
        
        print(f"\n{'='*80}")
        if result['success']:
            print("✅ TOUR RECOMMENDATION THÀNH CÔNG!")
            print(f"{'='*80}")
            
            # Optimizer info
            optimizer = result.get('optimizer_used', 'unknown')
            print(f"\n🔧 Optimizer: {optimizer.upper()}")
            
            if result.get('note'):
                print(f"📝 Note: {result['note']}")
            
            # Tour summary
            print(f"\n📊 TOUR SUMMARY:")
            print(f"   📍 Số địa điểm: {result['total_locations']}")
            print(f"   ⏱️  Tổng thời gian: {result['total_time']} phút ({result['total_time']/60:.1f} giờ)")
            print(f"   📏 Tổng khoảng cách: {result['total_distance']} km")
            print(f"   💰 Tổng chi phí: {result['total_cost']:,} VNĐ")
            print(f"   🎯 Tổng điểm: {result['total_score']:.3f}")
            print(f"   📊 Điểm trung bình: {result['avg_score']:.3f}")
            
            # Route details
            print(f"\n🗺️  CHI TIẾT LỘNH:")
            for i, loc in enumerate(result['route'], 1):
                print(f"\n   {i}. {loc['name']}")
                print(f"      🚗 Di chuyển: {loc['travel_time']} phút")
                print(f"      ⏱️  Tham quan: {loc['visit_time']} phút")
                print(f"      💰 Chi phí: {loc['price']:,} VNĐ")
                print(f"      🎯 Điểm: {loc['score']:.3f}")
                if loc.get('opening_hours'):
                    print(f"      🕐 Giờ mở cửa: {loc['opening_hours']}")
            
            print(f"\n{'='*80}")
            print("✅ TEST PASSED!")
            
        else:
            print("❌ TOUR RECOMMENDATION THẤT BẠI!")
            print(f"{'='*80}")
            print(f"   Message: {result.get('message', 'Unknown error')}")
            print(f"\n{'='*80}")
            print("❌ TEST FAILED!")
        
    except Exception as e:
        print(f"\n{'='*80}")
        print("❌ EXCEPTION OCCURRED!")
        print(f"{'='*80}")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_tour_recommendation()

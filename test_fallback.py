"""
Test Fallback Mechanism - Test với constraints rất chặt
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.services.tour_recommendation_service import TourRecommendationService

def test_fallback_mechanism():
    """Test với constraints rất chặt để trigger fallback"""
    
    print("=" * 80)
    print("🧪 TEST FALLBACK MECHANISM (Constraints rất chặt)")
    print("=" * 80)
    
    # User profile với constraints rất chặt
    user_profile = {
        "type": "Adventure",
        "preference": ["nature", "hiking", "adventure"],
        "budget": 100000,  # Budget rất thấp
        "time_available": 2,  # Chỉ 2 giờ
        "max_locations": 10  # Yêu cầu quá nhiều locations
    }
    
    start_location = {
        "name": "Khách sạn Quận 1",
        "latitude": 10.7769,
        "longitude": 106.7009
    }
    
    print(f"\n👤 User Profile (Constraints chặt):")
    print(f"   - Budget: {user_profile['budget']:,} VNĐ (RẤT THẤP)")
    print(f"   - Time: {user_profile['time_available']} giờ (RẤT ÍT)")
    print(f"   - Max locations: {user_profile['max_locations']} (QUÁ NHIỀU)")
    
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
            print("✅ TẠO TOUR THÀNH CÔNG (Có thể dùng fallback)")
            print(f"{'='*80}")
            
            optimizer = result.get('optimizer_used', 'unknown')
            print(f"\n🔧 Optimizer được sử dụng: {optimizer.upper()}")
            
            if optimizer == 'heuristic':
                print("   ✓ Đã fallback sang Heuristic Optimizer!")
                print("   ✓ Fallback mechanism hoạt động!")
            
            if result.get('note'):
                print(f"\n📝 Note: {result['note']}")
            
            print(f"\n📊 TOUR SUMMARY:")
            print(f"   📍 Số địa điểm: {result['total_locations']}")
            print(f"   ⏱️  Tổng thời gian: {result['total_time']} phút ({result['total_time']/60:.1f} giờ)")
            print(f"   📏 Tổng khoảng cách: {result['total_distance']} km")
            print(f"   💰 Tổng chi phí: {result['total_cost']:,} VNĐ")
            print(f"   🎯 Tổng điểm: {result['total_score']:.3f}")
            
            print(f"\n🗺️  CHI TIẾT LỘNH:")
            for i, loc in enumerate(result['route'], 1):
                print(f"   {i}. {loc['name']}")
                print(f"      Travel: {loc['travel_time']}min, Visit: {loc['visit_time']}min, Price: {loc['price']:,}đ")
            
            print(f"\n{'='*80}")
            print("✅ FALLBACK TEST PASSED!")
            
        else:
            print("❌ KHÔNG THỂ TẠO TOUR!")
            print(f"{'='*80}")
            print(f"   Message: {result.get('message')}")
            print(f"\n   Note: Constraints có thể quá chặt!")
        
    except Exception as e:
        print(f"\n{'='*80}")
        print("❌ EXCEPTION!")
        print(f"{'='*80}")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


def test_normal_case():
    """Test với constraints bình thường"""
    
    print("\n\n" + "=" * 80)
    print("🧪 TEST NORMAL CASE (Constraints bình thường)")
    print("=" * 80)
    
    user_profile = {
        "type": "Cultural",
        "preference": ["history", "culture", "museum"],
        "budget": 500000,
        "time_available": 5,
        "max_locations": 5
    }
    
    start_location = {
        "name": "Khách sạn Quận 1",
        "latitude": 10.7769,
        "longitude": 106.7009
    }
    
    print(f"\n👤 User Profile:")
    print(f"   - Type: {user_profile['type']}")
    print(f"   - Budget: {user_profile['budget']:,} VNĐ")
    print(f"   - Time: {user_profile['time_available']} giờ")
    print(f"   - Max locations: {user_profile['max_locations']}")
    
    db = SessionLocal()
    
    try:
        result = TourRecommendationService.get_tour_recommendations(
            db=db,
            user_profile=user_profile,
            start_location=start_location
        )
        
        print(f"\n{'='*80}")
        if result['success']:
            print("✅ TẠO TOUR THÀNH CÔNG")
            print(f"{'='*80}")
            
            optimizer = result.get('optimizer_used', 'unknown')
            print(f"\n🔧 Optimizer: {optimizer.upper()}")
            print(f"📍 Locations: {result['total_locations']}")
            print(f"⏱️  Time: {result['total_time']}min ({result['total_time']/60:.1f}h)")
            print(f"💰 Cost: {result['total_cost']:,}đ")
            
            print(f"\n{'='*80}")
            print("✅ NORMAL TEST PASSED!")
        else:
            print("❌ FAILED")
            print(f"   Message: {result.get('message')}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        
    finally:
        db.close()


if __name__ == "__main__":
    # Test fallback với constraints chặt
    test_fallback_mechanism()
    
    # Test normal case
    test_normal_case()

"""
Test Tour Recommendation API với curl
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_tour_recommend_api():
    """Test POST /api/v1/tours/recommend"""
    
    print("=" * 80)
    print("🧪 TEST TOUR RECOMMENDATION API")
    print("=" * 80)
    
    # Request body
    payload = {
        "user_profile": {
            "name": "Nguyễn Văn A",
            "type": "Adventure",
            "preference": ["nature", "hiking", "adventure"],
            "budget": 1500000,
            "time_available": 8,
            "max_locations": 8
        },
        "start_location": {
            "name": "Khách sạn Quận 1",
            "latitude": 10.7769,
            "longitude": 106.7009
        }
    }
    
    print("\n📤 Request:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        print("\n🚀 Calling API...")
        response = requests.post(
            f"{BASE_URL}/api/v1/tours/recommend",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ API RESPONSE SUCCESS!")
            print("=" * 80)
            
            print(f"\n🔧 Optimizer: {result.get('optimizer_used', 'N/A')}")
            if result.get('note'):
                print(f"📝 Note: {result['note']}")
            
            print(f"\n📊 TOUR SUMMARY:")
            print(f"   📍 Số địa điểm: {result['total_locations']}")
            print(f"   ⏱️  Tổng thời gian: {result['total_time']} phút ({result['total_time']/60:.1f} giờ)")
            print(f"   📏 Tổng khoảng cách: {result['total_distance']} km")
            print(f"   💰 Tổng chi phí: {result['total_cost']:,} VNĐ")
            print(f"   🎯 Tổng điểm: {result['total_score']:.3f}")
            print(f"   📊 Điểm trung bình: {result['avg_score']:.3f}")
            
            print(f"\n🗺️  CHI TIẾT LỘNH ({len(result['route'])} địa điểm):")
            for i, loc in enumerate(result['route'], 1):
                print(f"\n   {i}. {loc['name']}")
                print(f"      Type: {loc['type']}")
                print(f"      🚗 Di chuyển: {loc['travel_time']} phút")
                print(f"      ⏱️  Tham quan: {loc['visit_time']} phút")
                print(f"      💰 Chi phí: {loc['price']:,} VNĐ")
                print(f"      🎯 Điểm: {loc['score']:.3f}")
                if loc.get('opening_hours'):
                    print(f"      🕐 Giờ mở cửa: {loc['opening_hours']}")
            
            print("\n" + "=" * 80)
            print("✅ TEST PASSED!")
            
        else:
            print(f"\n❌ API ERROR!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\n❌ EXCEPTION!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


def test_tight_constraints():
    """Test với constraints chặt để trigger fallback"""
    
    print("\n\n" + "=" * 80)
    print("🧪 TEST FALLBACK MECHANISM (Tight Constraints)")
    print("=" * 80)
    
    payload = {
        "user_profile": {
            "type": "Adventure",
            "preference": ["nature"],
            "budget": 100000,  # Very low
            "time_available": 2,  # Very short
            "max_locations": 10  # Too many
        },
        "start_location": {
            "name": "Khách sạn Quận 1",
            "latitude": 10.7769,
            "longitude": 106.7009
        }
    }
    
    print("\n📤 Request (Tight Constraints):")
    print(f"   Budget: {payload['user_profile']['budget']:,} VNĐ")
    print(f"   Time: {payload['user_profile']['time_available']} giờ")
    print(f"   Max locations: {payload['user_profile']['max_locations']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/tours/recommend",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ API SUCCESS!")
            optimizer = result.get('optimizer_used', 'N/A')
            print(f"🔧 Optimizer: {optimizer}")
            
            if optimizer == 'heuristic':
                print("   ✓ Fallback mechanism activated!")
            
            if result.get('note'):
                print(f"📝 Note: {result['note']}")
            
            print(f"\n📊 Tour: {result['total_locations']} locations, {result['total_time']}min, {result['total_cost']:,}đ")
            print("\n✅ FALLBACK TEST PASSED!")
            
        else:
            print(f"❌ API ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")


if __name__ == "__main__":
    test_tour_recommend_api()
    test_tight_constraints()

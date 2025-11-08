"""
==============================================================================
PHÂN TÍCH SCORING - Xem chi tiết điểm số của các địa điểm
==============================================================================
File này giúp bạn hiểu rõ tại sao một địa điểm được chọn/không được chọn
"""

from tour_optimizer import (
    DestinationLoader,
    ScoringEngine
)
import json


def analyze_scores(user: dict, destinations: list, top_n: int = 10):
    """
    Phân tích điểm chi tiết cho từng địa điểm
    
    Args:
        user: User profile
        destinations: Danh sách địa điểm
        top_n: Số địa điểm top cần hiển thị
    """
    print("\n" + "="*80)
    print(f"📊 PHÂN TÍCH ĐIỂM CHO USER: {user.get('name', 'Unknown')}")
    print("="*80)
    
    print(f"\n👤 User Profile:")
    print(f"  • Loại: {user['type']}")
    print(f"  • Sở thích: {', '.join(user['preference'])}")
    print(f"  • Budget: {user['budget']:,.0f} VNĐ")
    print(f"  • Thời gian: {user['time_available']} giờ")
    
    # Tính điểm cho tất cả địa điểm
    scored = ScoringEngine.rank_destinations(user, destinations, None)
    
    print(f"\n📈 TOP {top_n} ĐỊA ĐIỂM CÓ ĐIỂM CAO NHẤT:")
    print("-" * 80)
    
    for i, (dest, score) in enumerate(scored[:top_n], 1):
        print(f"\n{i}. {dest['name']} (ID: {dest['id']})")
        print(f"   📍 Điểm tổng: {score:.3f}")
        print(f"   🏷️  Type: {dest['type']}")
        print(f"   🏷️  Tags: {', '.join(dest['tags'][:5])}")
        print(f"   💰 Giá: {dest['price']:,.0f} VNĐ")
        print(f"   ⏰ Thời gian tham quan: {dest['visit_time']} phút")
        print(f"   🔥 Trend: {dest['trend']}")
        print(f"   ✨ Novelty: {dest['novelty']}")
        print(f"   🛡️  Safety: {dest['safety']}")
        
        # Tính chi tiết từng thành phần điểm
        breakdown = calculate_score_breakdown(user, dest)
        print(f"   📊 Chi tiết điểm:")
        for component, value in breakdown.items():
            print(f"      • {component}: {value:.3f}")
    
    print("\n" + "="*80)
    
    # Phân tích địa điểm bị loại
    low_scored = scored[-5:]
    print(f"\n❌ 5 ĐỊA ĐIỂM CÓ ĐIỂM THẤP NHẤT:")
    print("-" * 80)
    
    for dest, score in low_scored:
        print(f"  • {dest['name']}: {score:.3f} điểm")
        print(f"    Lý do: ", end="")
        
        reasons = []
        if dest['price'] > user['budget']:
            reasons.append("Vượt budget")
        if dest['type'].lower() not in user['type'].lower():
            reasons.append("Type không khớp")
        if not set([t.lower() for t in dest['tags']]) & set([p.lower() for p in user['preference']]):
            reasons.append("Tags không khớp")
        if dest['trend'] == 'low':
            reasons.append("Trend thấp")
        
        if reasons:
            print(", ".join(reasons))
        else:
            print("Điểm các thành phần tổng hợp thấp")


def calculate_score_breakdown(user: dict, place: dict) -> dict:
    """Tính chi tiết từng thành phần điểm"""
    breakdown = {}
    
    # Type matching
    user_type = user.get('type', '').lower()
    place_type = place.get('type', '').lower()
    if user_type in place_type or place_type in user_type:
        breakdown['Type match'] = ScoringEngine.WEIGHTS['type']
    else:
        breakdown['Type match'] = 0
    
    # Tag similarity
    user_prefs = set([p.lower() for p in user.get('preference', [])])
    place_tags = set([t.lower() for t in place.get('tags', [])])
    if place_tags:
        tag_match = len(user_prefs & place_tags) / len(place_tags)
        breakdown['Tag similarity'] = tag_match * ScoringEngine.WEIGHTS['tags']
    else:
        breakdown['Tag similarity'] = 0
    
    # Trend
    trend = place.get('trend', 'low')
    breakdown['Trend'] = ScoringEngine.TREND_SCORE.get(trend, 0) * ScoringEngine.WEIGHTS['trend']
    
    # Novelty
    novelty = place.get('novelty', 'Low')
    user_novelty_pref = ScoringEngine.NOVELTY_PREFERENCE.get(user.get('type'), 0.5)
    breakdown['Novelty'] = ScoringEngine.NOVELTY_SCORE.get(novelty, 0) * ScoringEngine.WEIGHTS['novelty'] * user_novelty_pref
    
    # Safety
    safety = place.get('safety', 0.5)
    user_safety_pref = ScoringEngine.SAFETY_PREFERENCE.get(user.get('type'), 0.5)
    breakdown['Safety'] = safety * ScoringEngine.WEIGHTS['safety'] * user_safety_pref
    
    # Price
    price = place.get('price', 0)
    budget = user.get('budget', float('inf'))
    if budget > 0:
        price_score = max(0, 1 - (price / budget))
        breakdown['Price fit'] = price_score * ScoringEngine.WEIGHTS['price']
    else:
        breakdown['Price fit'] = ScoringEngine.WEIGHTS['price'] if price == 0 else 0
    
    # Time fit
    visit_time = place.get('visit_time', 60)
    time_available = user.get('time_available', 480) * 60
    if time_available > 0:
        time_fit = min(visit_time / time_available, 1.0)
        breakdown['Time fit'] = time_fit * ScoringEngine.WEIGHTS['time_fit']
    else:
        breakdown['Time fit'] = 0
    
    return breakdown


def compare_users(users: list, destinations: list):
    """So sánh điểm của cùng một địa điểm với các user khác nhau"""
    print("\n" + "="*80)
    print("🔄 SO SÁNH ĐIỂM GIỮA CÁC USER")
    print("="*80)
    
    # Lấy 5 địa điểm đầu tiên để so sánh
    sample_destinations = destinations[:5]
    
    for dest in sample_destinations:
        print(f"\n📍 {dest['name']}")
        print("-" * 80)
        
        scores = []
        for user in users:
            score = ScoringEngine.calculate_score(user, dest)
            scores.append((user['name'], user['type'], score))
        
        # Sort by score
        scores.sort(key=lambda x: x[2], reverse=True)
        
        for name, user_type, score in scores:
            bars = "█" * int(score * 50)
            print(f"  {name:20s} ({user_type:15s}): {score:.3f} {bars}")


def main():
    """Chạy phân tích"""
    
    # Load destinations
    destinations = DestinationLoader.load_destinations('destinations_data.json')
    destinations = DestinationLoader.filter_active_destinations(destinations)
    
    # Định nghĩa các user để phân tích
    users = [
        {
            'name': 'Adventure Lover',
            'type': 'Adventure',
            'preference': ['nature', 'adventure', 'hiking', 'water', 'photography'],
            'budget': 1000000,
            'time_available': 10,
            'max_locations': 5
        },
        {
            'name': 'Culture Enthusiast',
            'type': 'Cultural',
            'preference': ['culture', 'history', 'museum', 'art', 'architecture'],
            'budget': 500000,
            'time_available': 6,
            'max_locations': 4
        },
        {
            'name': 'Family Traveler',
            'type': 'Family',
            'preference': ['family', 'kids', 'park', 'safe', 'fun'],
            'budget': 800000,
            'time_available': 8,
            'max_locations': 4
        }
    ]
    
    # Phân tích từng user
    for user in users:
        analyze_scores(user, destinations, top_n=8)
        print("\n")
    
    # So sánh giữa các user
    compare_users(users, destinations)


if __name__ == '__main__':
    main()

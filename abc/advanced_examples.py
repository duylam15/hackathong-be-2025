"""
==============================================================================
ADVANCED EXAMPLES - Các ví dụ nâng cao
==============================================================================
Demos về cách tùy chỉnh và mở rộng hệ thống
"""

from tour_optimizer import (
    TourPlanner,
    ScoringEngine,
    DistanceCalculator,
    RouteOptimizer
)
import json


# ==============================================================================
# EXAMPLE 1: Tùy chỉnh trọng số scoring cho từng user cụ thể
# ==============================================================================

def example_1_custom_weights():
    """Ví dụ về cách thay đổi trọng số scoring"""
    print("\n" + "="*70)
    print("EXAMPLE 1: TÙY CHỈNH TRỌNG SỐ SCORING")
    print("="*70)
    
    # Backup trọng số gốc
    original_weights = ScoringEngine.WEIGHTS.copy()
    
    # User ưu tiên price và safety hơn các yếu tố khác
    custom_weights = {
        'type': 0.15,
        'tags': 0.15,
        'trend': 0.05,
        'novelty': 0.05,
        'safety': 0.25,  # Tăng safety
        'price': 0.30,   # Tăng price
        'time_fit': 0.05
    }
    
    print("\n📊 Trọng số mặc định:")
    print(json.dumps(original_weights, indent=2))
    
    print("\n📊 Trọng số tùy chỉnh:")
    print(json.dumps(custom_weights, indent=2))
    
    # Apply custom weights
    ScoringEngine.WEIGHTS = custom_weights
    
    # Run planning với weights mới
    planner = TourPlanner('destinations_data.json')
    
    user = {
        'name': 'Budget Safety User',
        'type': 'Family',
        'preference': ['family', 'safe', 'budget'],
        'budget': 300000,
        'time_available': 6,
        'max_locations': 4
    }
    
    result = planner.plan_tour(user)
    TourPlanner.print_tour_result(result, user)
    
    # Restore original weights
    ScoringEngine.WEIGHTS = original_weights
    
    print("\n✅ Đã restore trọng số về mặc định")


# ==============================================================================
# EXAMPLE 2: So sánh kết quả với các tốc độ di chuyển khác nhau
# ==============================================================================

def example_2_different_speeds():
    """Ví dụ về cách thay đổi tốc độ di chuyển"""
    print("\n" + "="*70)
    print("EXAMPLE 2: SO SÁNH VỚI CÁC TỐC ĐỘ DI CHUYỂN")
    print("="*70)
    
    user = {
        'name': 'Speed Test User',
        'type': 'Adventure',
        'preference': ['nature', 'adventure'],
        'budget': 1000000,
        'time_available': 10,
        'max_locations': 5
    }
    
    speeds = [30, 40, 60]  # km/h
    
    for speed in speeds:
        print(f"\n🚗 Tốc độ: {speed} km/h")
        print("-" * 70)
        
        # Tạo custom distance calculator với tốc độ khác
        class CustomDistanceCalculator(DistanceCalculator):
            @staticmethod
            def calculate_travel_time(distance_km: float, speed_kmh: float = speed) -> int:
                return int((distance_km / speed_kmh) * 60)
        
        # Tạm thời thay thế trong RouteOptimizer
        # (Trong thực tế, nên refactor để inject dependency)
        original_method = DistanceCalculator.calculate_travel_time
        DistanceCalculator.calculate_travel_time = CustomDistanceCalculator.calculate_travel_time
        
        planner = TourPlanner('destinations_data.json')
        result = planner.plan_tour(user)
        
        if result['success']:
            print(f"  ✅ Số địa điểm: {result['total_locations']}")
            print(f"  ⏰ Tổng thời gian: {result['total_time']} phút")
            print(f"  🚗 Thời gian di chuyển: {result['total_distance']} phút")
        
        # Restore
        DistanceCalculator.calculate_travel_time = original_method


# ==============================================================================
# EXAMPLE 3: Multi-day tour (nhiều ngày)
# ==============================================================================

def example_3_multi_day_tour():
    """Ví dụ về cách lên kế hoạch tour nhiều ngày"""
    print("\n" + "="*70)
    print("EXAMPLE 3: TOUR NHIỀU NGÀY")
    print("="*70)
    
    planner = TourPlanner('destinations_data.json')
    
    user = {
        'name': 'Multi-day Traveler',
        'type': 'Cultural',
        'preference': ['culture', 'history', 'art'],
        'budget': 2000000,  # 2 triệu
        'time_available': 8,  # 8 giờ mỗi ngày
        'max_locations': 6
    }
    
    num_days = 3
    
    print(f"\n📅 Lên kế hoạch cho {num_days} ngày")
    
    visited_ids = set()
    all_results = []
    
    for day in range(1, num_days + 1):
        print(f"\n{'='*70}")
        print(f"NGÀY {day}")
        print('='*70)
        
        # Lọc bỏ các địa điểm đã visit
        available_destinations = [
            d for d in planner.destinations 
            if d['id'] not in visited_ids
        ]
        
        if not available_destinations:
            print("❌ Không còn địa điểm mới để tham quan")
            break
        
        # Tạm thời thay thế destinations
        original_destinations = planner.destinations
        planner.destinations = available_destinations
        
        # Planning cho ngày này
        daily_user = user.copy()
        daily_user['name'] = f"{user['name']} - Ngày {day}"
        daily_user['max_locations'] = user['max_locations'] // num_days + 1
        
        result = planner.plan_tour(daily_user)
        
        if result['success']:
            TourPlanner.print_tour_result(result, daily_user)
            
            # Lưu lại IDs đã visit
            for stop in result['route']:
                visited_ids.add(stop['id'])
            
            all_results.append(result)
        else:
            print(f"❌ Không tìm thấy lộ trình cho ngày {day}")
        
        # Restore
        planner.destinations = original_destinations
    
    # Tổng kết
    print(f"\n{'='*70}")
    print(f"📊 TỔNG KẾT {num_days} NGÀY")
    print('='*70)
    
    total_locations = sum(r['total_locations'] for r in all_results)
    total_time = sum(r['total_time'] for r in all_results)
    total_cost = sum(r['total_cost'] for r in all_results)
    total_score = sum(r['total_score'] for r in all_results)
    
    print(f"  • Tổng số địa điểm: {total_locations}")
    print(f"  • Tổng thời gian: {total_time} phút ({total_time//60}h {total_time%60}m)")
    print(f"  • Tổng chi phí: {total_cost:,.0f} VNĐ")
    print(f"  • Tổng điểm: {total_score:.2f}")


# ==============================================================================
# EXAMPLE 4: Export kết quả ra các định dạng khác nhau
# ==============================================================================

def example_4_export_formats():
    """Ví dụ về cách export kết quả"""
    print("\n" + "="*70)
    print("EXAMPLE 4: EXPORT KẾT QUẢ")
    print("="*70)
    
    planner = TourPlanner('destinations_data.json')
    
    user = {
        'name': 'Export Test User',
        'type': 'Cultural',
        'preference': ['culture', 'history'],
        'budget': 500000,
        'time_available': 6,
        'max_locations': 4
    }
    
    result = planner.plan_tour(user)
    
    if not result['success']:
        print("❌ Không có kết quả để export")
        return
    
    # 1. Export JSON
    print("\n📄 1. Export JSON:")
    output = {
        'user': user,
        'tour': result
    }
    with open('tour_export.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("  ✅ Đã lưu: tour_export.json")
    
    # 2. Export CSV (đơn giản)
    print("\n📄 2. Export CSV:")
    csv_lines = ['STT,Tên,Giờ đến,Giờ rời,Thời gian tham quan,Chi phí,Điểm']
    for i, stop in enumerate(result['route'], 1):
        arrival = TourPlanner.format_time(stop['arrival_time'])
        departure = TourPlanner.format_time(stop['arrival_time'] + stop['visit_time'])
        csv_lines.append(
            f"{i},{stop['name']},{arrival},{departure},"
            f"{stop['visit_time']},{stop['cost']},{stop['score']}"
        )
    
    with open('tour_export.csv', 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_lines))
    print("  ✅ Đã lưu: tour_export.csv")
    
    # 3. Export Markdown
    print("\n📄 3. Export Markdown:")
    md_lines = [
        f"# Tour Du Lịch - {user['name']}",
        "",
        "## Thông Tin User",
        f"- **Loại**: {user['type']}",
        f"- **Budget**: {user['budget']:,.0f} VNĐ",
        f"- **Thời gian**: {user['time_available']} giờ",
        "",
        "## Tổng Quan",
        f"- Số địa điểm: {result['total_locations']}",
        f"- Tổng thời gian: {result['total_time']} phút",
        f"- Tổng chi phí: {result['total_cost']:,.0f} VNĐ",
        f"- Tổng điểm: {result['total_score']}",
        "",
        "## Lộ Trình Chi Tiết",
        ""
    ]
    
    for i, stop in enumerate(result['route'], 1):
        arrival = TourPlanner.format_time(stop['arrival_time'])
        departure = TourPlanner.format_time(stop['arrival_time'] + stop['visit_time'])
        md_lines.extend([
            f"### {i}. {stop['name']}",
            f"- ⏰ Đến: {arrival} | Rời: {departure}",
            f"- 💰 Chi phí: {stop['cost']:,.0f} VNĐ",
            f"- ⭐ Điểm: {stop['score']}",
            ""
        ])
    
    with open('tour_export.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    print("  ✅ Đã lưu: tour_export.md")
    
    # 4. Export HTML (đơn giản)
    print("\n📄 4. Export HTML:")
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tour Du Lịch - {user['name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c3e50; }}
        .info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .stop {{ border-left: 4px solid #3498db; padding-left: 15px; margin: 15px 0; }}
        .stop h3 {{ color: #2980b9; margin: 5px 0; }}
    </style>
</head>
<body>
    <h1>🗺️ Tour Du Lịch - {user['name']}</h1>
    
    <div class="info">
        <h2>👤 Thông Tin User</h2>
        <p><strong>Loại:</strong> {user['type']}</p>
        <p><strong>Budget:</strong> {user['budget']:,} VNĐ</p>
        <p><strong>Thời gian:</strong> {user['time_available']} giờ</p>
    </div>
    
    <div class="info">
        <h2>📈 Tổng Quan</h2>
        <p><strong>Số địa điểm:</strong> {result['total_locations']}</p>
        <p><strong>Tổng thời gian:</strong> {result['total_time']} phút</p>
        <p><strong>Tổng chi phí:</strong> {result['total_cost']:,} VNĐ</p>
        <p><strong>Tổng điểm:</strong> {result['total_score']}</p>
    </div>
    
    <h2>🗺️ Lộ Trình Chi Tiết</h2>
"""
    
    for i, stop in enumerate(result['route'], 1):
        arrival = TourPlanner.format_time(stop['arrival_time'])
        departure = TourPlanner.format_time(stop['arrival_time'] + stop['visit_time'])
        html += f"""
    <div class="stop">
        <h3>{i}. {stop['name']}</h3>
        <p>⏰ Đến: {arrival} | Rời: {departure}</p>
        <p>💰 Chi phí: {stop['cost']:,} VNĐ | ⭐ Điểm: {stop['score']}</p>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open('tour_export.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("  ✅ Đã lưu: tour_export.html")
    
    print(f"\n{'='*70}")
    print("✅ Đã export tất cả các định dạng!")


# ==============================================================================
# EXAMPLE 5: Batch processing - Xử lý nhiều users cùng lúc
# ==============================================================================

def example_5_batch_processing():
    """Ví dụ về xử lý hàng loạt users"""
    print("\n" + "="*70)
    print("EXAMPLE 5: BATCH PROCESSING")
    print("="*70)
    
    planner = TourPlanner('destinations_data.json')
    
    # Load nhiều users từ file hoặc database
    users = [
        {
            'name': 'User 1',
            'type': 'Adventure',
            'preference': ['nature', 'hiking'],
            'budget': 1000000,
            'time_available': 8,
            'max_locations': 5
        },
        {
            'name': 'User 2',
            'type': 'Cultural',
            'preference': ['culture', 'museum'],
            'budget': 500000,
            'time_available': 6,
            'max_locations': 4
        },
        {
            'name': 'User 3',
            'type': 'Family',
            'preference': ['family', 'kids'],
            'budget': 800000,
            'time_available': 7,
            'max_locations': 4
        }
    ]
    
    results = []
    
    print(f"\n🚀 Xử lý {len(users)} users...")
    
    for i, user in enumerate(users, 1):
        print(f"\n[{i}/{len(users)}] Processing {user['name']}...", end=" ")
        
        result = planner.plan_tour(user)
        
        if result['success']:
            print("✅")
            results.append({
                'user': user,
                'tour': result
            })
        else:
            print("❌")
    
    # Export batch results
    with open('batch_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Đã xử lý {len(results)}/{len(users)} users thành công")
    print("💾 Kết quả đã lưu: batch_results.json")
    
    # Statistics
    print("\n📊 THỐNG KÊ:")
    print("-" * 70)
    
    for item in results:
        user = item['user']
        tour = item['tour']
        print(f"  {user['name']:15s}: "
              f"{tour['total_locations']} địa điểm, "
              f"{tour['total_cost']:,} VNĐ, "
              f"điểm {tour['avg_score']:.2f}")


# ==============================================================================
# MAIN - Chạy tất cả examples
# ==============================================================================

def main():
    """Chạy tất cả examples"""
    
    examples = [
        ("Tùy chỉnh trọng số", example_1_custom_weights),
        ("Tốc độ di chuyển", example_2_different_speeds),
        ("Tour nhiều ngày", example_3_multi_day_tour),
        ("Export formats", example_4_export_formats),
        ("Batch processing", example_5_batch_processing),
    ]
    
    print("\n" + "="*70)
    print("🎓 ADVANCED EXAMPLES")
    print("="*70)
    print("\nChọn example để chạy:")
    
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  0. Chạy tất cả")
    
    try:
        choice = input("\nNhập số (0-5): ").strip()
        
        if choice == '0':
            for name, func in examples:
                print(f"\n\n{'='*70}")
                print(f"▶️  Chạy: {name}")
                print('='*70)
                func()
        elif choice in ['1', '2', '3', '4', '5']:
            idx = int(choice) - 1
            examples[idx][1]()
        else:
            print("❌ Lựa chọn không hợp lệ")
    
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")


if __name__ == '__main__':
    main()

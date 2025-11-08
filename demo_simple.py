"""
==============================================================================
DEMO ĐƠN GIẢN - Gợi ý tour du lịch cho một user cụ thể
==============================================================================
File này giúp bạn nhanh chóng test với user profile tùy chỉnh
"""

from tour_optimizer import TourPlanner

def main():
    """Chạy demo với user tùy chỉnh"""
    
    # Khởi tạo planner
    planner = TourPlanner('destinations_data.json')
    
    # ===== TÙY CHỈNH USER PROFILE Ở ĐÂY =====
    user = {
        'name': 'Demo User',
        
        # Loại user: 'Adventure', 'Cultural', 'Family', 'Relaxation', 'Budget'
        'type': 'Adventure',
        
        # Sở thích (tags)
        'preference': [
            'nature',
            'adventure', 
            'hiking',
            'photography',
            'water'
        ],
        
        # Budget (VNĐ)
        'budget': 1500000,  # 1.5 triệu
        
        # Thời gian có (giờ)
        'time_available': 12,
        
        # Số lượng địa điểm tối đa muốn tham quan
        'max_locations': 6
    }
    
    # ===== ĐIỂM KHỞI HÀNH (Tùy chọn) =====
    # Trung tâm TP. Hồ Chí Minh (Quận 1)
    start_location = {
        'id': 0,
        'name': 'Khách sạn của tôi (Quận 1, TP.HCM)',
        'latitude': 10.7769,
        'longitude': 106.7009,
        'visit_time': 0,
        'price': 0
    }
    
    # ===== CHẠY PLANNING =====
    print("\n🚀 Bắt đầu lên kế hoạch tour...")
    result = planner.plan_tour(user, start_location)
    
    # ===== IN KẾT QUẢ =====
    TourPlanner.print_tour_result(result, user)
    
    # ===== XUẤT RA JSON (Tùy chọn) =====
    if result['success']:
        import json
        
        # Tạo output JSON
        output = {
            'user': user,
            'tour': result
        }
        
        # Lưu vào file
        with open('tour_result.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print("\n💾 Kết quả đã được lưu vào file: tour_result.json")


if __name__ == '__main__':
    main()

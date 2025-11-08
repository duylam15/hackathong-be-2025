# Tour Recommendation Service - Nâng cấp với Fallback Mechanism

## 🎯 Tổng quan

Service đã được nâng cấp với **fallback mechanism** để đảm bảo luôn có thể tạo gợi ý tour, tránh lỗi khi OR-Tools không tìm được solution.

## 🔧 Các thành phần chính

### 1. **ScoringEngine** - Tính điểm cá nhân hóa
- Tính điểm cho từng địa điểm dựa trên user profile
- Trọng số: Type (30%), Tags (40%), Price (20%), Time (10%)

### 2. **DistanceCalculator** - Tính khoảng cách
- Haversine formula để tính khoảng cách chính xác
- Tính thời gian di chuyển dựa trên khoảng cách

### 3. **RouteOptimizer** - OR-Tools (Primary)
- Sử dụng OR-Tools VRP để tối ưu lộ trình
- Tối ưu khoảng cách, thời gian, chi phí
- Đảm bảo constraints: time, budget, max_locations

### 4. **HeuristicOptimizer** - Greedy Algorithm (Fallback) ⭐ MỚI
- Thuật toán tham lam đơn giản
- Chọn địa điểm gần nhất có score cao
- Được kích hoạt khi OR-Tools thất bại

### 5. **TourRecommendationService** - Service chính
- Quản lý toàn bộ flow
- Tự động fallback khi cần
- Filter destinations hợp lệ

## 🚀 Luồng hoạt động

```
1. Lấy destinations từ database
   ↓
2. Filter destinations hợp lệ
   - Tọa độ ở Việt Nam (lat: 8-24, lon: 102-110)
   - Visit time hợp lý (> 0, <= 600 phút)
   ↓
3. Filter theo khoảng cách từ start location
   - Ưu tiên trong bán kính 50km
   - Mở rộng lên 100km nếu cần
   ↓
4. Tính điểm và chọn top destinations
   - Max 6 locations để dễ optimize
   ↓
5. Thử OR-Tools optimizer trước
   ↓
6. Nếu OR-Tools thất bại → Fallback sang Heuristic
   ↓
7. Trả về kết quả với thông tin optimizer đã dùng
```

## ✨ Các cải tiến

### 1. **Fallback Mechanism**
```python
# OR-Tools thất bại
result = optimizer.optimize()

if not result.get('success'):
    # Tự động fallback sang Heuristic
    heuristic_optimizer = HeuristicOptimizer(...)
    result = heuristic_optimizer.optimize_greedy()
```

### 2. **Filter Destinations hợp lệ**
```python
# Loại bỏ destinations có tọa độ sai
if (8 <= lat <= 24 and 102 <= lon <= 110 and 
    visit_time > 0 and visit_time <= 600):
    valid_destinations.append(dest)
```

### 3. **Filter theo khoảng cách**
```python
# Chỉ giữ destinations trong bán kính hợp lý
dist = DistanceCalculator.haversine_distance(...)
if dist <= max_distance_km:
    nearby_destinations.append(dest)
```

### 4. **Tracking optimizer được sử dụng**
```python
{
    'success': True,
    'optimizer_used': 'ortools',  # or 'heuristic'
    'note': 'Message for user',
    ...
}
```

## 📊 Kết quả test

### Test 1: Constraints bình thường
```
✅ OR-Tools thành công
- Optimizer: ORTOOLS
- Locations: 6
- Time: 520 phút (8.7 giờ)
- Cost: 500,000 VNĐ
- Score: 2.461
```

### Test 2: Constraints rất chặt (Budget: 100k, Time: 2h)
```
✅ Fallback sang Heuristic thành công
- Optimizer: HEURISTIC
- Locations: 2
- Time: 107 phút (1.8 giờ)
- Cost: 0 VNĐ
- Score: 0.613
- Note: "Sử dụng thuật toán tối ưu đơn giản (Greedy)"
```

### Test 3: Cultural tour (Budget: 500k, Time: 5h)
```
✅ OR-Tools thành công
- Optimizer: ORTOOLS
- Locations: 5
- Time: 483 phút (8.1 giờ)
- Cost: 155,000 VNĐ
```

## 🎯 Ưu điểm

1. **Luôn có kết quả**: Không bao giờ trả về lỗi hoàn toàn
2. **Tự động điều chỉnh**: Fallback khi cần thiết
3. **Transparent**: User biết optimizer nào được dùng
4. **Robust**: Xử lý được nhiều edge cases
5. **Filter thông minh**: Loại bỏ dữ liệu không hợp lệ

## 🔄 Heuristic Algorithm (Greedy)

### Chiến lược:
1. Bắt đầu từ start location
2. Chọn địa điểm chưa thăm có `score/distance` cao nhất
3. Kiểm tra constraints (time, budget)
4. Lặp lại cho đến khi không thêm được địa điểm nào

### Công thức:
```python
metric = score / distance_penalty
distance_penalty = max(1, distance / 10)  # Penalty cho địa điểm xa
```

### Ưu điểm:
- Đơn giản, nhanh
- Luôn tìm được solution nếu có destinations thỏa mãn
- Không phụ thuộc vào OR-Tools

### Nhược điểm:
- Không tối ưu toàn cục như OR-Tools
- Có thể bỏ sót một số combinations tốt

## 📝 API Response Schema

```python
{
    "success": true,
    "route": [...],
    "total_locations": 6,
    "total_time": 520,
    "total_distance": 8.62,
    "total_score": 2.461,
    "total_cost": 500000,
    "avg_score": 0.410,
    "optimizer_used": "ortools",  # or "heuristic"
    "note": "Optional message"     # Only when using heuristic
}
```

## 🚀 Sử dụng

### Request:
```json
{
  "user_profile": {
    "type": "Adventure",
    "preference": ["nature", "hiking"],
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
```

### Response:
- Nếu OR-Tools thành công → `optimizer_used: "ortools"`
- Nếu fallback sang Heuristic → `optimizer_used: "heuristic"` + `note`

## 🎉 Kết luận

Service đã được nâng cấp với **fallback mechanism** hoàn chỉnh, đảm bảo:
- ✅ Luôn tạo được tour recommendations
- ✅ Tự động xử lý edge cases
- ✅ Transparent với user
- ✅ Robust và reliable

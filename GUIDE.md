# 🎓 HƯỚNG DẪN CHI TIẾT - Hệ Thống Gợi Ý Tour Du Lịch

## 📚 Mục Lục
1. [Tổng Quan](#tổng-quan)
2. [Cài Đặt](#cài-đặt)
3. [Cách Sử Dụng](#cách-sử-dụng)
4. [Cấu Trúc Code](#cấu-trúc-code)
5. [Thuật Toán](#thuật-toán)
6. [Tùy Chỉnh](#tùy-chỉnh)
7. [FAQ](#faq)

---

## 🎯 Tổng Quan

Hệ thống này giải quyết bài toán **Vehicle Routing Problem (VRP)** trong du lịch với các đặc điểm:

### Bài Toán
- **Input**: User profile + Database địa điểm
- **Output**: Lộ trình tối ưu thỏa mãn ràng buộc
- **Mục tiêu**: Tối đa hóa điểm hấp dẫn, thỏa mãn budget & thời gian

### Pipeline Xử Lý

```
1. Load Data
   ↓
2. Calculate Scores (Scoring Engine)
   ↓
3. Filter Feasible Locations
   ↓
4. Build Distance Matrix
   ↓
5. Optimize Route (OR-Tools VRP)
   ↓
6. Extract & Format Result
```

---

## 🛠️ Cài Đặt

### Bước 1: Clone/Download Project

```bash
cd /path/to/HackathonSGU2025
```

### Bước 2: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `ortools>=9.7.0` - OR-Tools cho tối ưu hóa
- Python 3.8+

### Bước 3: Verify Installation

```bash
python3 -c "from ortools.constraint_solver import pywrapcp; print('✅ OK')"
```

---

## 🚀 Cách Sử Dụng

### 1️⃣ Chạy Demo Nhanh

```bash
python3 tour_optimizer.py
```

Chương trình sẽ chạy với 5 user profiles mẫu và in kết quả.

### 2️⃣ Tùy Chỉnh User (Đơn Giản)

Sửa file `demo_simple.py`:

```python
user = {
    'name': 'Tên của bạn',
    'type': 'Adventure',  # Loại user
    'preference': ['nature', 'hiking'],  # Sở thích
    'budget': 1000000,  # Budget (VNĐ)
    'time_available': 8,  # Thời gian (giờ)
    'max_locations': 5  # Số địa điểm tối đa
}
```

Chạy:

```bash
python3 demo_simple.py
```

Kết quả sẽ được lưu vào `tour_result.json`.

### 3️⃣ Phân Tích Scoring

```bash
python3 analyze_scoring.py
```

Xem chi tiết tại sao một địa điểm có điểm cao/thấp.

### 4️⃣ Sử Dụng Trong Code Của Bạn

```python
from tour_optimizer import TourPlanner

# Khởi tạo
planner = TourPlanner('destinations_data.json')

# Định nghĩa user
user = {
    'name': 'John',
    'type': 'Cultural',
    'preference': ['museum', 'history'],
    'budget': 500000,
    'time_available': 6,
    'max_locations': 4
}

# Planning
result = planner.plan_tour(user)

# In kết quả
TourPlanner.print_tour_result(result, user)

# Hoặc xử lý result (dict)
if result['success']:
    for stop in result['route']:
        print(f"{stop['name']}: {stop['arrival_time']} phút")
```

---

## 📁 Cấu Trúc Code

### File Structure

```
HackathonSGU2025/
├── tour_optimizer.py          # Main program (toàn bộ logic)
├── demo_simple.py             # Demo đơn giản, dễ tùy chỉnh
├── analyze_scoring.py         # Phân tích điểm
├── destinations_data.json     # Database địa điểm
├── requirements.txt           # Dependencies
├── README.md                  # Tài liệu chính
└── GUIDE.md                   # File này
```

### Module trong `tour_optimizer.py`

#### 1. **DestinationLoader**
```python
# Load dữ liệu từ JSON
destinations = DestinationLoader.load_destinations('file.json')

# Parse opening hours
start, end = DestinationLoader.parse_opening_hours("08:00-17:30")
# => (480, 1050) phút
```

#### 2. **ScoringEngine**
```python
# Tính điểm cho 1 địa điểm
score = ScoringEngine.calculate_score(user, place)

# Rank tất cả địa điểm
ranked = ScoringEngine.rank_destinations(user, places, top_n=10)
```

#### 3. **DistanceCalculator**
```python
# Tính khoảng cách giữa 2 điểm
dist = DistanceCalculator.haversine_distance(lat1, lon1, lat2, lon2)

# Build ma trận khoảng cách
matrix = DistanceCalculator.build_distance_matrix(locations)
```

#### 4. **RouteOptimizer**
```python
# Tối ưu lộ trình
optimizer = RouteOptimizer(destinations, user, start_location)
result = optimizer.optimize()
```

#### 5. **TourPlanner**
```python
# Main integration
planner = TourPlanner('data.json')
result = planner.plan_tour(user)
```

---

## 🧮 Thuật Toán

### 1. Scoring Algorithm

**Công thức:**

$$
Score = \sum_{i=1}^{7} w_i \times s_i
$$

Với:
- $w_i$: Trọng số thành phần i
- $s_i$: Điểm thành phần i (0-1)

**7 Thành phần:**

| Thành phần | Trọng số | Cách tính |
|------------|----------|-----------|
| Type Match | 25% | 1 nếu khớp, 0 nếu không |
| Tag Similarity | 25% | Jaccard similarity |
| Trend | 15% | high=1.0, medium=0.6, low=0.3 |
| Novelty | 10% | Điều chỉnh theo user type |
| Safety | 10% | Điều chỉnh theo user type |
| Price Fit | 10% | 1 - (price/budget) |
| Time Fit | 5% | min(visit_time/available, 1) |

**Ví dụ:**

```
User: Adventure, budget=1M, time=10h
Place: Vịnh Hạ Long, price=500k, visit=8h

- Type match: 0.25 (khớp)
- Tag similarity: 0.25 * 0.8 = 0.20 (4/5 tags khớp)
- Trend: 0.15 * 1.0 = 0.15 (high)
- Novelty: 0.10 * 1.0 = 0.10 (high, Adventure ưa novelty)
- Safety: 0.10 * 0.3 * 0.85 = 0.026 (Adventure ít quan tâm safety)
- Price fit: 0.10 * 0.5 = 0.05 (500k/1M)
- Time fit: 0.05 * 0.8 = 0.04 (8h/10h)

Total: 0.816
```

### 2. VRP Optimization (OR-Tools)

**Model:**

```
Objective: Maximize Σ(score_i × visited_i)

Subject to:
  1. Σ(travel_time + visit_time) ≤ max_time
  2. Σ(price_i × visited_i) ≤ budget
  3. Σ(visited_i) ≤ max_locations
  4. arrival_i ∈ [opening_i, closing_i]  (soft)
  5. Start and end at depot
```

**Solver:**
- **Method**: Guided Local Search
- **Time Limit**: 10 seconds
- **First Solution**: Path Cheapest Arc

**Tại sao chọn OR-Tools?**
- ✅ Hỗ trợ VRP với multiple constraints
- ✅ Fast (C++ backend)
- ✅ Open source, free
- ✅ Active development by Google

---

## 🎨 Tùy Chỉnh

### 1. Thay Đổi Trọng Số Scoring

Trong `tour_optimizer.py`, class `ScoringEngine`:

```python
WEIGHTS = {
    'type': 0.30,      # Tăng ưu tiên type matching
    'tags': 0.30,
    'trend': 0.20,
    'novelty': 0.05,
    'safety': 0.05,
    'price': 0.05,
    'time_fit': 0.05
}
```

### 2. Thay Đổi Tốc Độ Di Chuyển

Trong `DistanceCalculator.calculate_travel_time()`:

```python
return int((distance_km / 50) * 60)  # 50 km/h thay vì 40
```

### 3. Thêm Địa Điểm Mới

Thêm vào `destinations_data.json`:

```json
{
  "id": 16,
  "company_id": 100,
  "name": "Địa điểm mới",
  "type": "Adventure",
  "tags": ["tag1", "tag2"],
  "latitude": 21.0000,
  "longitude": 105.0000,
  "location_address": "Địa chỉ",
  "novelty": "High",
  "safety": 0.9,
  "price": 100000,
  "opening_hours": "08:00-18:00",
  "visit_time": 120,
  "trend": "high",
  "facilities": ["parking"],
  "metadata": {"rating": 4.5},
  "popularity_score": 80,
  "is_active": true
}
```

### 4. Thêm Loại User Mới

Cập nhật mapping trong `ScoringEngine`:

```python
NOVELTY_PREFERENCE = {
    'Adventure': 1.0,
    'Cultural': 0.6,
    'Family': 0.4,
    'Relaxation': 0.3,
    'Budget': 0.3,
    'Luxury': 0.7,  # Mới thêm
}

SAFETY_PREFERENCE = {
    'Family': 1.0,
    'Relaxation': 0.8,
    'Cultural': 0.7,
    'Budget': 0.5,
    'Adventure': 0.3,
    'Luxury': 0.9,  # Mới thêm
}
```

### 5. Thay Đổi Solver Parameters

Trong `RouteOptimizer.optimize()`:

```python
search_parameters.time_limit.seconds = 30  # Tăng thời gian search

# Thử solver khác
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.TABU_SEARCH
)
```

---

## ❓ FAQ

### Q1: Tại sao time windows không được enforce chặt?

**A:** Time windows được implement như soft constraints để tránh bài toán trở nên infeasible. Trong thực tế, khách du lịch có thể linh hoạt thay đổi giờ tham quan.

Nếu muốn hard constraints:

```python
time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
```

Nhưng có thể không tìm được solution.

### Q2: Làm sao tăng số địa điểm trong tour?

**A:** 
1. Tăng `max_locations` trong user profile
2. Tăng `time_available`
3. Tăng `budget`
4. Giảm trọng số `price` và `time_fit` trong scoring

### Q3: Kết quả không khả thi (vượt budget)?

**A:** Kiểm tra:
- Budget có đủ cho ít nhất 1 địa điểm không?
- Thử tăng penalty trong `AddDisjunction`
- Kiểm tra budget constraint có được add đúng không

Debug:

```python
print(f"Max budget: {max_budget}")
print(f"Min price: {min([p for p in self.costs if p > 0])}")
```

### Q4: Làm sao xử lý dependencies giữa địa điểm?

**A:** Thêm precedence constraints:

```python
# Ví dụ: Phải đi địa điểm A trước địa điểm B
routing.solver().Add(
    time_dimension.CumulVar(index_A) <= 
    time_dimension.CumulVar(index_B)
)
```

### Q5: Làm sao thêm multiple tours (nhiều ngày)?

**A:** Tăng `num_vehicles` và thêm constraints:

```python
data['num_vehicles'] = 3  # 3 ngày

# Add time constraints cho mỗi vehicle (ngày)
for vehicle_id in range(3):
    routing.solver().Add(
        time_dimension.CumulVar(routing.End(vehicle_id)) <= 480
    )  # Mỗi ngày <= 8 giờ
```

### Q6: Performance chậm với nhiều địa điểm?

**A:** Tối ưu:
1. Giảm `top_n` trong filtering
2. Giảm `time_limit` của solver
3. Dùng first solution strategy đơn giản hơn:

```python
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
)
```

### Q7: Làm sao integrate với Google Maps API?

**A:** Thay thế `DistanceCalculator`:

```python
import googlemaps

gmaps = googlemaps.Client(key='YOUR_API_KEY')

def get_real_distance(origin, destination):
    result = gmaps.distance_matrix(origin, destination, mode='driving')
    duration = result['rows'][0]['elements'][0]['duration']['value']
    return duration // 60  # Convert to minutes
```

---

## 📞 Support

Nếu gặp lỗi hoặc cần hỗ trợ:

1. Check logs/error messages
2. Verify input data format
3. Test với dữ liệu mẫu trước
4. Kiểm tra version của OR-Tools

---

## 🎓 Học Thêm

### OR-Tools Resources
- [OR-Tools Documentation](https://developers.google.com/optimization)
- [VRP Guide](https://developers.google.com/optimization/routing/vrp)
- [Time Windows Example](https://developers.google.com/optimization/routing/vrptw)

### Algorithms
- [Vehicle Routing Problem (Wikipedia)](https://en.wikipedia.org/wiki/Vehicle_routing_problem)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [Local Search Algorithms](https://en.wikipedia.org/wiki/Local_search_(optimization))

---

**Happy Coding! 🚀**

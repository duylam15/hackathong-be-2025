# 📘 Hướng Dẫn Chi Tiết: Endpoint `/recommend` - Tour Recommendation API

## 📌 Tổng Quan

Endpoint `/recommend` là API chính để **tạo gợi ý tour du lịch cá nhân hóa** dựa trên:
- **User profile**: Loại du khách, sở thích, ngân sách, thời gian
- **Start location** (optional): Điểm khởi hành
- **AI-powered optimization**: Sử dụng OR-Tools hoặc thuật toán tham lam

**Endpoint**: `POST /api/v1/tours/recommend`

---

## 🔧 Kiến Trúc Tổng Thể

```
┌─────────────────┐
│  Client Request │
│  (TourRequest)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│         API Endpoint Layer                  │
│   /api/v1/endpoints/tours.py               │
│                                             │
│   • Nhận TourRequest                       │
│   • Convert Pydantic models → dict         │
│   • Gọi TourRecommendationService          │
│   • Trả về TourRecommendation              │
└────────┬────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│              Service Layer                               │
│   app/services/tour_recommendation_service.py           │
│                                                          │
│   ┌────────────────────────────────────────────────┐   │
│   │  1. ScoringEngine                               │   │
│   │     • calculate_score()                        │   │
│   │     • rank_destinations()                      │   │
│   │     Tính điểm cá nhân hóa cho từng địa điểm  │   │
│   └────────────────────────────────────────────────┘   │
│                                                          │
│   ┌────────────────────────────────────────────────┐   │
│   │  2. DistanceCalculator                         │   │
│   │     • haversine_distance()                     │   │
│   │     • calculate_travel_time()                  │   │
│   │     • build_distance_matrix()                  │   │
│   │     Tính khoảng cách và thời gian di chuyển   │   │
│   └────────────────────────────────────────────────┘   │
│                                                          │
│   ┌────────────────────────────────────────────────┐   │
│   │  3. RouteOptimizer (OR-Tools)                  │   │
│   │     • optimize() - Vehicle Routing Problem     │   │
│   │     • Tối ưu với Time Windows, Budget         │   │
│   │     Tìm lộ trình tối ưu nhất                  │   │
│   └────────────────────────────────────────────────┘   │
│                                                          │
│   ┌────────────────────────────────────────────────┐   │
│   │  4. HeuristicOptimizer (Fallback)              │   │
│   │     • optimize_greedy()                        │   │
│   │     Thuật toán tham lam khi OR-Tools fail     │   │
│   └────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│    Database     │
│  (Destinations) │
└─────────────────┘
```

---

## 📥 Request Format

### Request Body: `TourRequest`

```json
{
  "user_profile": {
    "name": "Nguyễn Văn A",
    "type": "Adventure",
    "preference": ["nature", "hiking", "adventure", "photography"],
    "budget": 1500000,
    "time_available": 8,
    "max_locations": 5
  },
  "start_location": {
    "name": "Khách sạn Quận 1",
    "latitude": 10.7769,
    "longitude": 106.7009
  }
}
```

### Request Fields Chi Tiết

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_profile.type` | enum | ✅ | Loại du khách: `Adventure`, `Cultural`, `Family`, `Relaxation`, `Budget` |
| `user_profile.preference` | list[str] | ✅ | Sở thích: `["nature", "hiking", "culture", "history", ...]` |
| `user_profile.budget` | int | ✅ | Ngân sách (VNĐ) |
| `user_profile.time_available` | int | ✅ | Thời gian có sẵn (giờ) |
| `user_profile.max_locations` | int | ❌ | Số địa điểm tối đa (mặc định: 5) |
| `start_location` | object | ❌ | Điểm khởi hành (mặc định: Quận 1, TP.HCM) |

---

## 🔄 Quy Trình Xử Lý (Step-by-Step)

### **Step 1: API Endpoint Layer** (`tours.py`)

```python
@router.post("/recommend", response_model=TourRecommendation)
def get_tour_recommendation(request: TourRequest, db: Session = Depends(get_db)):
```

**Nhiệm vụ:**
1. **Validate input** với Pydantic models
2. **Convert StartLocation** sang dictionary:
   ```python
   start_loc_dict = {
       'id': 0,
       'name': request.start_location.name,
       'latitude': request.start_location.latitude,
       'longitude': request.start_location.longitude,
       'visit_time': 0,
       'price': 0
   }
   ```
3. **Convert UserProfile** sang dictionary:
   ```python
   user_dict = request.user_profile.model_dump()
   ```
4. **Gọi service**:
   ```python
   result = TourRecommendationService.get_tour_recommendations(
       db=db,
       user_profile=user_dict,
       start_location=start_loc_dict
   )
   ```
5. **Handle errors** và trả về response

---

### **Step 2: Service Layer - Main Flow**

#### 2.1. Query Database
```python
destinations = db.query(Destination).filter(Destination.is_active == True).all()
```
- Lấy tất cả địa điểm đang active
- Convert sang dictionary với `to_dict()`

#### 2.2. Data Validation & Filtering
```python
# Lọc địa điểm hợp lệ (tọa độ Vietnam, visit_time hợp lý)
valid_destinations = []
for dest in destinations:
    lat, lon = dest['latitude'], dest['longitude']
    visit_time = dest['visit_time']
    
    # Vietnam: latitude 8-24, longitude 102-110
    if (8 <= lat <= 24 and 102 <= lon <= 110 and 
        0 < visit_time <= 600):  # Max 10 hours
        valid_destinations.append(dest)
```

#### 2.3. Distance Filtering
```python
# Chỉ giữ địa điểm trong bán kính 50km (hoặc 100km nếu không đủ)
nearby_destinations = []
max_distance_km = 50

for dest in valid_destinations:
    dist = DistanceCalculator.haversine_distance(
        start_lat, start_lon,
        dest['latitude'], dest['longitude']
    )
    if dist <= max_distance_km:
        nearby_destinations.append(dest)
```

---

### **Step 3: Scoring Engine - Tính Điểm Cá Nhân Hóa**

#### 3.1. Công Thức Tính Điểm

```python
score = 0.0

# 1. Type Matching (30%)
if user_type in place_type:
    score += 0.30

# 2. Tag Similarity (40%) - Jaccard Similarity
intersection = len(user_prefs & place_tags)
union = len(user_prefs | place_tags)
tag_similarity = intersection / union
score += 0.40 * tag_similarity

# 3. Price Fit (20%)
if price <= budget * 0.3:      # Rẻ → 20%
    score += 0.20
elif price <= budget * 0.5:    # Trung bình → 16%
    score += 0.16
elif price <= budget:          # Trong budget → 10%
    score += 0.10

# 4. Time Fit (10%)
time_ratio = min(visit_time / time_available, 1.0)
score += 0.10 * (1 - time_ratio * 0.5)

return score  # 0.0 - 1.0
```

#### 3.2. Ví Dụ Thực Tế

**User Profile:**
- Type: `Adventure`
- Preference: `["nature", "hiking", "adventure"]`
- Budget: 1,500,000 VNĐ
- Time available: 8 giờ = 480 phút

**Destination A:**
- Type: `Nature Park`
- Tags: `["nature", "hiking", "outdoor"]`
- Price: 200,000 VNĐ
- Visit time: 120 phút

**Tính điểm:**
```
1. Type: "Adventure" không match "Nature Park" → 0.0
2. Tags: {nature, hiking, adventure} ∩ {nature, hiking, outdoor} = 2
         {nature, hiking, adventure} ∪ {nature, hiking, outdoor} = 4
         Similarity = 2/4 = 0.5 → 0.40 × 0.5 = 0.20
3. Price: 200K ≤ 450K (30% of 1.5M) → 0.20
4. Time: 120/480 = 0.25 → 0.10 × (1 - 0.25×0.5) = 0.0875

Total score = 0.0 + 0.20 + 0.20 + 0.0875 = 0.4875
```

#### 3.3. Ranking
```python
scored = ScoringEngine.rank_destinations(
    user_profile,
    nearby_destinations,
    top_n=max_locations  # Lấy top 5-6 địa điểm
)
# Returns: [(destination, score)] sorted by score descending
```

---

### **Step 4: Route Optimization**

Sau khi có **top N destinations** với scores cao, hệ thống tối ưu lộ trình.

#### 4.1. OR-Tools Optimizer (Primary)

**OR-Tools** là thư viện tối ưu của Google, giải bài toán **Vehicle Routing Problem (VRP)**.

##### Components:

**a) Distance Matrix**
```python
# Ma trận khoảng cách (km) giữa tất cả locations
distance_matrix[i][j] = haversine_distance(loc_i, loc_j)

# Ví dụ với 4 locations (0=start, 1-3=destinations):
[[0.0,  5.2,  8.1,  3.4],    # From start
 [5.2,  0.0,  4.5,  6.8],    # From dest 1
 [8.1,  4.5,  0.0,  5.3],    # From dest 2
 [3.4,  6.8,  5.3,  0.0]]    # From dest 3
```

**b) Time Matrix**
```python
time_matrix[i][j] = travel_time + visit_time
# travel_time = distance_km / speed (40 km/h)
# visit_time = location j visit duration
```

**c) Constraints**

1. **Time Window Constraint**
   ```python
   routing.AddDimension(
       time_callback_index,
       0,  # No slack
       max_time * 3,  # Max total time
       True,
       'Time'
   )
   ```

2. **Budget Constraint**
   ```python
   routing.AddDimensionWithVehicleCapacity(
       cost_callback_index,
       0,
       [max_budget],  # Budget limit
       True,
       'Budget'
   )
   ```

**d) Objective Function**
```python
# Minimize total distance
routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)
```

**e) Search Strategy**
```python
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = AUTOMATIC
search_parameters.local_search_metaheuristic = AUTOMATIC
search_parameters.time_limit.seconds = 30
```

##### Ví Dụ Output:
```
Route found:
Start → Dest 2 (score: 0.85) → Dest 1 (score: 0.72) → Dest 3 (score: 0.68) → Start
Total distance: 18.5 km
Total time: 380 minutes (within 480 limit)
Total cost: 950,000 VNĐ (within 1,500,000 limit)
```

---

#### 4.2. Heuristic Optimizer (Fallback)

Nếu OR-Tools **không tìm được solution** (do constraints quá chặt), hệ thống fallback sang **thuật toán tham lam**.

##### Strategy:

```python
def optimize_greedy():
    route = []
    current = start_location
    visited = set()
    
    while len(route) < max_locations:
        best_dest = None
        best_metric = -1
        
        for dest in destinations:
            if dest.id in visited:
                continue
            
            # Calculate distance & time
            distance = haversine_distance(current, dest)
            travel_time = calculate_travel_time(distance)
            
            # Check constraints
            if total_time + travel_time > max_time:
                continue
            if total_cost + dest.price > max_budget:
                continue
            
            # Metric: score / distance_penalty
            # Ưu tiên: gần + điểm cao
            distance_penalty = max(1, distance / 10)
            metric = dest.score / distance_penalty
            
            if metric > best_metric:
                best_metric = metric
                best_dest = dest
        
        if best_dest is None:
            break  # No more valid destinations
        
        route.append(best_dest)
        visited.add(best_dest.id)
        current = best_dest
    
    return route
```

##### Ưu/Nhược Điểm:

| Aspect | OR-Tools | Heuristic |
|--------|----------|-----------|
| **Tối ưu** | Global optimal | Local optimal |
| **Tốc độ** | Chậm (≤30s) | Nhanh (<1s) |
| **Constraints** | Xử lý phức tạp | Đơn giản |
| **Use case** | Production | Fallback |

---

### **Step 5: Response Construction**

```python
return {
    'success': True,
    'route': [
        {
            'id': 1,
            'name': 'Vườn Quốc gia Cát Tiên',
            'type': 'Nature Park',
            'latitude': 11.4219,
            'longitude': 107.4256,
            'location_address': 'Đồng Nai',
            'price': 200000,
            'visit_time': 180,
            'travel_time': 45,
            'score': 0.85,
            'opening_hours': '07:00 - 17:00',
            'facilities': ['parking', 'restaurant', 'guide'],
            'images': ['url1', 'url2']
        },
        # ... more locations
    ],
    'total_locations': 5,
    'total_time': 420,  # minutes
    'total_distance': 68.5,  # km
    'total_score': 3.75,
    'total_cost': 950000,  # VNĐ
    'avg_score': 0.75,
    'optimizer_used': 'ortools',  # or 'heuristic'
    'note': None  # or "Sử dụng thuật toán tối ưu đơn giản..."
}
```

---

## 📊 Performance & Complexity

### Time Complexity

| Component | Complexity | Description |
|-----------|------------|-------------|
| Database Query | O(N) | N = số địa điểm trong DB |
| Scoring | O(N × M) | M = số tags/preferences |
| Distance Filtering | O(N) | Haversine cho mỗi địa điểm |
| OR-Tools | O(2^N) | Worst case (NP-hard) |
| Heuristic | O(N²) | Greedy selection |

### Typical Response Time

- **Fast path** (Heuristic): 0.5 - 2 seconds
- **Optimal path** (OR-Tools): 5 - 30 seconds
- **Database query**: < 0.5 seconds

---

## 🎯 Use Cases

### 1. Adventure Tour
```json
{
  "user_profile": {
    "type": "Adventure",
    "preference": ["nature", "hiking", "mountain"],
    "budget": 2000000,
    "time_available": 10
  }
}
```
→ Nhận được tour với national parks, hiking trails, outdoor activities

### 2. Family Tour
```json
{
  "user_profile": {
    "type": "Family",
    "preference": ["family-friendly", "entertainment", "safe"],
    "budget": 3000000,
    "time_available": 8
  }
}
```
→ Nhận được tour với theme parks, museums, zoos

### 3. Budget Traveler
```json
{
  "user_profile": {
    "type": "Budget",
    "preference": ["cheap", "local", "walking"],
    "budget": 500000,
    "time_available": 6
  }
}
```
→ Nhận được tour với free attractions, local markets, walking tours

---

## ⚠️ Error Handling

### Common Errors

```python
# 1. No valid destinations
{
  "success": False,
  "message": "Không có địa điểm hợp lệ trong hệ thống"
}

# 2. No nearby destinations
{
  "success": False,
  "message": "Không có địa điểm nào trong bán kính 100km"
}

# 3. OR-Tools + Heuristic both failed
{
  "success": False,
  "message": "Không thể tạo tour với các ràng buộc hiện tại"
}
```

### Troubleshooting

**Q: Tại sao không có kết quả?**
- Kiểm tra `budget` và `time_available` có quá thấp không
- Thử mở rộng `max_locations` hoặc tăng budget
- Kiểm tra `start_location` có hợp lệ không

**Q: Kết quả không tối ưu?**
- Có thể đang dùng Heuristic optimizer (check `optimizer_used`)
- Thử giảm `max_locations` để OR-Tools dễ tìm solution hơn
- Điều chỉnh `preference` tags cho chính xác hơn

---

## 🔧 Configuration

### Tunable Parameters

```python
# In tour_recommendation_service.py

# Distance filtering
max_distance_km = 50  # or 100 km

# Scoring weights
WEIGHTS = {
    'type': 0.30,
    'tags': 0.40,
    'price': 0.20,
    'time_fit': 0.10
}

# OR-Tools timeout
search_parameters.time_limit.seconds = 30

# Travel speed
speed_kmh = 40  # Average city speed
```

---

## 📚 Related Endpoints

### `/analyze-scores`
Phân tích điểm của các địa điểm mà không tạo tour:
```bash
POST /api/v1/tours/analyze-scores
{
  "user_profile": {...},
  "top_n": 10
}
```

### `/quick-recommend`
Gợi ý nhanh với thông tin tối thiểu:
```bash
POST /api/v1/tours/quick-recommend
{
  "user_type": "Adventure",
  "budget": 1500000,
  "time_available": 8
}
```

---

## 🚀 Performance Tips

1. **Database Indexing**: Index `is_active`, `latitude`, `longitude` columns
2. **Caching**: Cache scored destinations cho popular profiles
3. **Async Processing**: Chạy OR-Tools trong background task
4. **Precompute**: Tính trước distance matrix cho common locations
5. **Load Balancing**: Distribute OR-Tools computation

---

## 📝 Summary

**Endpoint `/recommend`** là một hệ thống phức tạp kết hợp:
- ✅ **AI Scoring**: Tính điểm cá nhân hóa cho từng địa điểm
- ✅ **Distance Filtering**: Lọc địa điểm theo bán kính
- ✅ **OR-Tools Optimization**: Tối ưu lộ trình với constraints
- ✅ **Heuristic Fallback**: Đảm bảo luôn có kết quả
- ✅ **Smart Error Handling**: Xử lý edge cases gracefully

**Flow chính:**
```
Request → Validate → Query DB → Filter → Score → Rank → Optimize → Response
```

**Technology Stack:**
- FastAPI (Web framework)
- SQLAlchemy (ORM)
- OR-Tools (Route optimization)
- Pydantic (Data validation)
- Custom Heuristics (Fallback algorithm)

---

**Tác giả:** Hackathon Team  
**Ngày tạo:** November 2025  
**Version:** 1.0

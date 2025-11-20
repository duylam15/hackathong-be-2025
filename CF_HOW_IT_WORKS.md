# 📊 Collaborative Filtering - Cách Hoạt Động

## 🎯 TL;DR

**CÓ!** Collaborative Filtering cần **nhiều người dùng** và **nhiều dữ liệu tương tác** mới hoạt động tốt.

---

## 📈 Giai Đoạn Hoạt Động

### 1️⃣ Giai Đoạn THU THẬP DỮ LIỆU (Hiện tại)

**Trạng thái**: Đang ở giai đoạn này ✅

**Mục tiêu**: Thu thập càng nhiều dữ liệu user càng tốt:
- ✅ **Ratings**: User đánh giá địa điểm (1-5 sao)
- ✅ **Favorites**: User lưu địa điểm yêu thích
- ✅ **Visits**: User check-in khi đến địa điểm
- ✅ **Feedback**: User click, view, skip địa điểm

**API đang hoạt động**:
```javascript
// Thu thập dữ liệu
POST /api/v1/ratings/      // User đánh giá
POST /api/v1/favorites/    // User lưu yêu thích
POST /api/v1/visits/       // User check-in
POST /api/v1/feedback/     // Track hành vi
```

**Dữ liệu tối thiểu cần có**:
- 🔴 **Ít nhất 5-10 users** với hành vi khác nhau
- 🔴 **Mỗi user có 3-5 ratings** cho các địa điểm khác nhau
- 🔴 **Có sự chồng lấn**: User A và User B cùng rate một số địa điểm

---

### 2️⃣ Giai Đoạn TRAINING MODEL

**Trạng thái**: Chưa thực hiện (cần đủ dữ liệu trước)

**Khi nào training**:
- Khi có đủ dữ liệu (50+ ratings từ 10+ users)
- Định kỳ mỗi ngày/tuần (để cập nhật model)
- Khi có dữ liệu mới đáng kể

**Code sẽ chạy**:
```python
# File: app/services/collaborative_filtering_service.py
# Line: 198-250

class CollaborativeFilteringService:
    
    @staticmethod
    def train_model(db: Session):
        """Train collaborative filtering model"""
        
        # 1. Lấy tất cả ratings từ database
        ratings = db.query(DestinationRating).all()
        
        # 2. Build user-item matrix
        user_item_matrix = build_matrix(ratings)
        #    User 1: [5.0, 4.0, None, 3.5, ...]
        #    User 2: [None, 4.5, 5.0, None, ...]
        #    User 3: [4.0, None, 4.5, 5.0, ...]
        
        # 3. Train model (Matrix Factorization)
        model = train_svd_model(user_item_matrix)
        
        # 4. Lưu model vào file
        save_model(model, "cf_model.pkl")
        
        return model
```

**Thuật toán**:
- **SVD (Singular Value Decomposition)**: Phân tích ma trận user-item
- **ALS (Alternating Least Squares)**: Tối ưu hóa lặp
- **Neural CF**: Dùng neural network (nâng cao)

---

### 3️⃣ Giai Đoạn RECOMMENDATION

**Trạng thái**: Đã có code, chờ model ✅

**Khi model đã train xong**:
```python
# File: app/services/tour_recommendation_service.py
# Line: 50-120

class TourRecommendationService:
    
    @staticmethod
    def get_recommendations_with_cf(
        db: Session,
        user_id: int,
        user_profile: dict
    ):
        """Get tour recommendations using CF + Content-based"""
        
        # 1. Lấy user preferences từ ratings/favorites
        user_prefs = CollaborativeFilteringService.get_user_preferences(
            db, user_id
        )
        
        # 2. Dùng CF model để predict ratings cho các địa điểm chưa visit
        cf_predictions = CollaborativeFilteringService.predict_ratings(
            user_id, 
            unvisited_destinations
        )
        # Output: {destination_id: predicted_rating}
        # {101: 4.7, 102: 3.2, 103: 4.9, ...}
        
        # 3. Kết hợp với Content-based filtering
        final_scores = combine_cf_and_content(
            cf_predictions,
            user_profile,
            destination_features
        )
        
        # 4. Rank destinations theo điểm số
        ranked_destinations = sort_by_score(final_scores)
        
        # 5. Build tour từ top destinations
        tour = build_optimal_tour(
            ranked_destinations,
            user_profile.budget,
            user_profile.time_available
        )
        
        return tour
```

---

## 🔍 Collaborative Filtering - Chi Tiết Hoạt Động

### Cách CF Tìm Similar Users

```python
# Example: User similarity matrix
"""
Giả sử có 3 users và ratings của họ:

Destination:    D1    D2    D3    D4    D5
User 1:        5.0   4.0    -    3.5   4.5
User 2:         -    4.5   5.0    -    4.0
User 3:        4.0    -    4.5   5.0   3.5

CF sẽ tính similarity giữa các users:
- User 1 & User 3 giống nhau vì:
  + Cả 2 đều rate cao D1 (5.0 và 4.0)
  + Cả 2 đều rate cao D5 (4.5 và 3.5)
  
- Vậy nếu User 3 thích D4 (5.0) mà User 1 chưa rate
  => CF sẽ recommend D4 cho User 1 với predicted rating ~4.5
"""

def calculate_user_similarity(user1_ratings, user2_ratings):
    """Tính độ tương đồng giữa 2 users"""
    # Cosine Similarity
    common_items = get_common_rated_items(user1_ratings, user2_ratings)
    
    if len(common_items) < 2:
        return 0  # Không đủ dữ liệu để so sánh
    
    similarity = cosine_similarity(
        user1_ratings[common_items],
        user2_ratings[common_items]
    )
    return similarity

def predict_rating(user_id, destination_id, all_users_ratings):
    """Dự đoán rating của user cho destination chưa visit"""
    # 1. Tìm similar users
    similar_users = find_similar_users(user_id, all_users_ratings)
    # Output: [(user2, similarity=0.85), (user5, similarity=0.72), ...]
    
    # 2. Lấy ratings của similar users cho destination này
    weighted_sum = 0
    total_weight = 0
    
    for similar_user, similarity in similar_users:
        if similar_user.has_rated(destination_id):
            rating = similar_user.get_rating(destination_id)
            weighted_sum += rating * similarity
            total_weight += similarity
    
    # 3. Tính predicted rating (weighted average)
    if total_weight > 0:
        predicted_rating = weighted_sum / total_weight
    else:
        predicted_rating = 3.0  # Default rating
    
    return predicted_rating
```

---

## 📊 Ví Dụ Thực Tế

### Scenario: Du lịch Đà Nẵng

**Dữ liệu hiện tại** (giả sử):

```javascript
// User 1: Thích biển và thiên nhiên
{
  ratings: [
    { destination: "Bãi biển Mỹ Khê", rating: 5.0 },
    { destination: "Bán đảo Sơn Trà", rating: 4.5 },
    { destination: "Chùa Linh Ứng", rating: 4.0 }
  ]
}

// User 2: Thích văn hóa và lịch sử
{
  ratings: [
    { destination: "Bảo tàng Chăm", rating: 5.0 },
    { destination: "Phố cổ Hội An", rating: 5.0 },
    { destination: "Chùa Linh Ứng", rating: 4.0 }  // ← Cùng rate với User 1
  ]
}

// User 3: Thích biển (giống User 1)
{
  ratings: [
    { destination: "Bãi biển Mỹ Khê", rating: 5.0 },  // ← Cùng với User 1
    { destination: "Bán đảo Sơn Trà", rating: 4.0 },  // ← Cùng với User 1
    { destination: "Cù Lao Chàm", rating: 5.0 }       // ← User 1 chưa đi
  ]
}
```

**CF Recommendation cho User 1**:

```python
# CF phát hiện: User 1 và User 3 rất giống nhau
# - Cả 2 đều rate cao "Mỹ Khê" và "Sơn Trà"
# - Similarity = 0.92 (rất cao)

# User 3 rate "Cù Lao Chàm" = 5.0 mà User 1 chưa đi
# => CF predict: User 1 sẽ thích "Cù Lao Chàm" với rating ~4.8

# Kết quả: Recommend "Cù Lao Chàm" cho User 1
```

---

## 🚀 Flow Hoàn Chỉnh Khi Có Đủ Dữ Liệu

### Step 1: User Request Tour

```javascript
// Frontend gọi API
POST http://localhost:8000/api/v1/tours/recommend
{
  "user_profile": {
    "user_id": 1,  // ← Quan trọng!
    "name": "John",
    "type": "Beach",
    "preference": ["nature", "photography"],
    "budget": 2000000,
    "time_available": 8
  }
}
```

### Step 2: Backend Process

```python
# File: app/api/v1/endpoints/tours.py
@router.post("/recommend")
def recommend_tour(request: TourRequest, db: Session = Depends(get_database)):
    
    # 1. Check if user has history
    user_id = request.user_profile.get("user_id")
    
    if user_id:
        # 2. Get user's ratings/favorites/visits
        user_history = CollaborativeFilteringService.get_user_history(db, user_id)
        
        if len(user_history.ratings) >= 3:  # Đủ dữ liệu
            # 3. Use CF to get recommendations
            cf_destinations = CollaborativeFilteringService.get_cf_recommendations(
                db, user_id, limit=20
            )
            # Output: [
            #   {destination_id: 15, predicted_rating: 4.8},
            #   {destination_id: 23, predicted_rating: 4.5},
            #   ...
            # ]
            
            # 4. Boost CF recommendations in scoring
            for dest in cf_destinations:
                dest.score += dest.predicted_rating * 0.3  # CF weight
            
            # 5. Combine with content-based
            tour = TourRecommendationService.build_tour_with_cf(
                db,
                request.user_profile,
                cf_destinations
            )
        else:
            # Not enough data, use content-based only
            tour = TourRecommendationService.build_tour_content_based(
                db,
                request.user_profile
            )
    else:
        # No user_id, use content-based only
        tour = TourRecommendationService.build_tour_content_based(
            db,
            request.user_profile
        )
    
    return tour
```

### Step 3: CollaborativeFilteringService

```python
# File: app/services/collaborative_filtering_service.py

class CollaborativeFilteringService:
    
    @staticmethod
    def get_cf_recommendations(db: Session, user_id: int, limit: int = 20):
        """Get CF-based recommendations for user"""
        
        # 1. Load trained model
        model = load_model("cf_model.pkl")
        
        if not model:
            return []  # Model chưa train
        
        # 2. Get all destinations
        all_destinations = db.query(Destination).all()
        
        # 3. Get destinations user already rated/visited
        user_rated = db.query(DestinationRating)\
            .filter(DestinationRating.user_id == user_id)\
            .all()
        rated_ids = [r.destination_id for r in user_rated]
        
        # 4. Predict ratings for unrated destinations
        predictions = []
        for dest in all_destinations:
            if dest.id not in rated_ids:
                predicted_rating = model.predict(user_id, dest.id)
                predictions.append({
                    "destination_id": dest.id,
                    "destination": dest,
                    "predicted_rating": predicted_rating
                })
        
        # 5. Sort by predicted rating
        predictions.sort(key=lambda x: x["predicted_rating"], reverse=True)
        
        # 6. Return top N
        return predictions[:limit]
    
    @staticmethod
    def get_user_preferences(db: Session, user_id: int):
        """Get user preferences from history"""
        
        # 1. Get highly rated destinations
        high_ratings = db.query(DestinationRating)\
            .filter(
                DestinationRating.user_id == user_id,
                DestinationRating.rating >= 4.0
            )\
            .all()
        
        # 2. Get favorites
        favorites = db.query(UserFavorite)\
            .filter(UserFavorite.user_id == user_id)\
            .all()
        
        # 3. Get visit history
        visits = db.query(VisitLog)\
            .filter(
                VisitLog.user_id == user_id,
                VisitLog.completed == True
            )\
            .all()
        
        # 4. Extract patterns
        preferred_types = []
        preferred_tags = []
        
        for rating in high_ratings:
            dest = rating.destination
            preferred_types.append(dest.type)
            preferred_tags.extend(dest.tags)
        
        # 5. Return user profile
        return {
            "preferred_types": most_common(preferred_types),
            "preferred_tags": most_common(preferred_tags),
            "avg_rating": average([r.rating for r in high_ratings]),
            "total_visits": len(visits)
        }
```

---

## 🎯 Khi Nào CF Bắt Đầu Hoạt Động?

### Minimum Requirements

| Yêu cầu | Số lượng tối thiểu | Tối ưu |
|---------|-------------------|--------|
| **Users** | 5-10 users | 50+ users |
| **Ratings per user** | 3-5 ratings | 10+ ratings |
| **Total ratings** | 30-50 ratings | 500+ ratings |
| **Common items** | 2+ items được rate bởi nhiều users | 10+ items |

### Current Status Check

```python
# Check nếu đủ dữ liệu để train CF
def check_cf_readiness(db: Session):
    """Check if enough data to train CF"""
    
    # Count users with ratings
    users_with_ratings = db.query(
        func.count(func.distinct(DestinationRating.user_id))
    ).scalar()
    
    # Count total ratings
    total_ratings = db.query(func.count(DestinationRating.id)).scalar()
    
    # Count destinations with multiple ratings
    common_destinations = db.query(DestinationRating.destination_id)\
        .group_by(DestinationRating.destination_id)\
        .having(func.count(DestinationRating.id) >= 2)\
        .count()
    
    is_ready = (
        users_with_ratings >= 5 and
        total_ratings >= 30 and
        common_destinations >= 3
    )
    
    return {
        "ready": is_ready,
        "users_with_ratings": users_with_ratings,
        "total_ratings": total_ratings,
        "common_destinations": common_destinations,
        "message": "Ready to train CF model" if is_ready else "Need more data"
    }
```

---

## 📝 Tóm Tắt

### Hiện tại (Phase 1) - THU THẬP DỮ LIỆU ✅

```
User → Rating/Favorite/Visit → Database
                                    ↓
                            [Chưa đủ dữ liệu]
                                    ↓
                         Dùng Content-based only
```

**APIs hoạt động**:
- ✅ `POST /api/v1/ratings/` - Thu thập ratings
- ✅ `POST /api/v1/favorites/` - Thu thập favorites  
- ✅ `POST /api/v1/visits/` - Thu thập visits
- ✅ `POST /api/v1/feedback/` - Track behavior

### Tương lai (Phase 2) - COLLABORATIVE FILTERING 🚀

```
User → Request tour
        ↓
   [Enough data?]
        ↓
      YES
        ↓
   Load CF Model
        ↓
   Predict ratings for unvisited destinations
        ↓
   Combine with Content-based
        ↓
   Build optimal tour
        ↓
   Return personalized recommendations
```

**Khi hoạt động**:
- 🎯 CF model predict ratings
- 🎯 Recommend destinations similar users liked
- 🎯 Personalized tours based on user history
- 🎯 Better accuracy over time

---

## 🔧 Code Locations

### 1. CF Service
```
File: app/services/collaborative_filtering_service.py
Lines: 1-300
```

### 2. Tour Recommendation with CF
```
File: app/services/tour_recommendation_service.py
Lines: 50-200
```

### 3. Rating APIs
```
File: app/api/v1/endpoints/rating.py
Lines: 1-200
```

### 4. Check CF Readiness
```python
# Add this endpoint to check if ready to train
@router.get("/cf/status")
def get_cf_status(db: Session = Depends(get_database)):
    return CollaborativeFilteringService.check_readiness(db)
```

---

## ❓ FAQs

### Q: Khi nào CF bắt đầu hoạt động?
**A**: Khi có ≥5 users, mỗi user có ≥3 ratings, và ≥2 destinations được rate bởi nhiều users.

### Q: Nếu chưa đủ dữ liệu thì sao?
**A**: Hệ thống tự động fallback về Content-based filtering (dựa vào user_profile).

### Q: CF cần train thường xuyên không?
**A**: Nên train lại mỗi ngày/tuần khi có dữ liệu mới để cải thiện accuracy.

### Q: CF có thể hoạt động với 1 user không?
**A**: KHÔNG. CF cần nhiều users để tìm similarity patterns.

### Q: Làm sao test CF nhanh?
**A**: Tạo fake data với 10 users, mỗi user rate 5-10 destinations khác nhau.

---

## 🎓 Next Steps

1. ✅ **Thu thập dữ liệu** - Frontend gọi các CF APIs
2. ⏳ **Chờ đủ data** - Cần 5-10 users với 3-5 ratings mỗi người
3. 🔧 **Train model** - Chạy training script khi đủ data
4. 🚀 **Enable CF** - CF tự động được dùng trong recommendations
5. 📊 **Monitor** - Track accuracy và user satisfaction

---

**Kết luận**: CF cần thời gian và dữ liệu để hoạt động, nhưng APIs đã sẵn sàng để thu thập dữ liệu ngay bây giờ! 🎉

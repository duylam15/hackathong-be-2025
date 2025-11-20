# 🎯 Hướng Dẫn Train CF Model

## ❓ Tại Sao Chưa Có `cf_model.pkl`?

**Lý do**: Model CF chưa được train! Hiện tại bạn mới ở giai đoạn **thu thập dữ liệu**.

```
❌ File NOT found: cf_model.pkl
✅ Đang ở giai đoạn: Thu thập ratings/favorites/visits
⏳ Chờ đợi: Đủ dữ liệu để train model
```

---

## 📊 Check Trạng Thái Hiện Tại

### Cách 1: Quick Check (Nhanh)

```powershell
# Xem status nhanh
python check_cf_status.py
```

**Output mẫu**:
```
📊 CF MODEL STATUS CHECK
========================================
📈 Data Collected:
   Total users:              3
   Users with ratings:       2 ❌ (need ≥5)
   Total ratings:            8 ❌ (need ≥30)
   Total favorites:          4
   Total visits:             2
   Total destinations:       50
   Common destinations:      1 ❌ (need ≥3)

🧠 CF Model:
   Status:                   ❌ NOT TRAINED
   Model file:               Not found

🎯 Overall Status:
   ❌ NOT ENOUGH DATA YET

   What you need:
     • 3 more users with ratings
     • 22 more ratings
     • More overlap (users rating same destinations)
```

### Cách 2: Full Check với Training

```powershell
# Check và có thể train luôn
python train_cf_model.py
```

---

## 🎯 Yêu Cầu Tối Thiểu Để Train

| Metric | Tối Thiểu | Hiện Tại | Status |
|--------|-----------|----------|--------|
| **Users with ratings** | ≥ 5 | ? | ❌ |
| **Total ratings** | ≥ 30 | ? | ❌ |
| **Common destinations** | ≥ 3 | ? | ❌ |

**Common destinations**: Số lượng địa điểm được rate bởi ≥2 users (để tìm similarity)

---

## 🚀 Quy Trình Train Model

### Step 1: Thu Thập Đủ Dữ Liệu

**Cách thức**:
1. Mời 5-10 người test app
2. Mỗi người rate 3-5 địa điểm
3. Đảm bảo có overlap (cùng rate một số địa điểm)

**API để thu thập**:
```javascript
// Người dùng rate địa điểm
POST /api/v1/ratings/
{
  "user_id": 1,
  "destination_id": 5,
  "rating": 4.5,
  "review_text": "Great place!"
}

// Lưu yêu thích
POST /api/v1/favorites/
{
  "user_id": 1,
  "destination_id": 7
}

// Check-in visit
POST /api/v1/visits/
{
  "user_id": 1,
  "destination_id": 3,
  "visit_date": "2025-11-20T10:00:00",
  "completed": true
}
```

### Step 2: Check Status

```powershell
python check_cf_status.py
```

Chờ đến khi thấy:
```
✅ Users with ratings:       5 ✅
✅ Total ratings:            30 ✅
✅ Common destinations:      3 ✅
```

### Step 3: Train Model

```powershell
python train_cf_model.py
```

**Output mong đợi**:
```
🧠 TRAINING COLLABORATIVE FILTERING MODEL
==========================================

1️⃣ Building user-item interaction matrix...
   ✅ Matrix shape: (5, 50) (users × destinations)
   ✅ User IDs: [1, 2, 3, 4, 5]
   ✅ Destination IDs: [1, 2, 3, ..., 50]

2️⃣ Computing user-user similarities...
   ✅ User similarity matrix: (5, 5)

3️⃣ Computing item-item similarities...
   ✅ Item similarity matrix: (50, 50)

4️⃣ Saving model to disk...
   ✅ Model saved to: d:\Hackathon\backend\cf_model.pkl

📊 Model Statistics:
   • Number of users:        5
   • Number of destinations: 50
   • Number of ratings:      35
   • Matrix density:         14.00%
   • Trained at:             2025-11-20T15:30:00

✅ CF MODEL TRAINING COMPLETED!
```

### Step 4: Verify Model

```powershell
# Check lại status
python check_cf_status.py
```

Nên thấy:
```
🧠 CF Model:
   Status:                   ✅ TRAINED
   Trained at:               2025-11-20T15:30:00
   Users in model:           5
   Destinations in model:    50
   Total ratings:            35

🎯 Overall Status:
   ✅ CF MODEL IS READY TO USE!
```

### Step 5: Restart Server

```powershell
# CF model đã sẵn sàng, restart để áp dụng
uvicorn app.main:app --reload
```

---

## 📝 Ví Dụ Tạo Test Data

Nếu muốn test nhanh, tạo fake data:

```python
# File: create_test_cf_data.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import SessionLocal
from app.models.destination_rating import DestinationRating
from datetime import datetime
import random

db = SessionLocal()

# 5 users rate 5-10 destinations mỗi người
test_data = [
    # User 1: Thích biển và thiên nhiên
    (1, 1, 5.0), (1, 2, 4.5), (1, 5, 4.0), (1, 8, 3.5), (1, 10, 4.5),
    
    # User 2: Thích văn hóa
    (2, 3, 5.0), (2, 4, 4.5), (2, 6, 4.0), (2, 1, 4.0), (2, 7, 5.0),
    
    # User 3: Thích biển (giống User 1)
    (3, 1, 5.0), (3, 2, 4.0), (3, 5, 4.5), (3, 9, 5.0), (3, 11, 4.0),
    
    # User 4: Thích núi và adventure
    (4, 8, 5.0), (4, 9, 4.5), (4, 10, 4.0), (4, 12, 5.0), (4, 13, 4.5),
    
    # User 5: Mix (overlap với nhiều users)
    (5, 1, 4.5), (5, 3, 4.0), (5, 8, 4.5), (5, 9, 4.0), (5, 14, 5.0),
]

for user_id, dest_id, rating in test_data:
    rating_obj = DestinationRating(
        user_id=user_id,
        destination_id=dest_id,
        rating=rating,
        review_text=f"Test review from user {user_id}",
        visit_date=datetime.now(),
        created_date=datetime.now(),
        updated_date=datetime.now()
    )
    db.add(rating_obj)

db.commit()
print(f"✅ Created {len(test_data)} test ratings")
db.close()
```

Chạy:
```powershell
python create_test_cf_data.py
python check_cf_status.py  # Verify
python train_cf_model.py   # Train
```

---

## 🔄 Update Model (Định Kỳ)

Khi có thêm dữ liệu mới, nên train lại model:

```powershell
# Train lại với dữ liệu mới
python train_cf_model.py
```

**Khuyến nghị**:
- Train lại **mỗi ngày** nếu có nhiều users mới
- Train lại **mỗi tuần** nếu ít dữ liệu mới
- Train lại **khi có 50+ ratings mới**

---

## 🎯 Khi Nào CF Bắt Đầu Hoạt Động?

### Trước Khi Train (Hiện tại)

```javascript
// User request tour
POST /api/v1/tours/recommend
{
  "user_profile": {
    "user_id": 1,
    "type": "Beach",
    "preference": ["nature"],
    "budget": 2000000
  }
}

// Backend response
{
  "destinations": [...],
  "cf_used": false,  // ❌ CF không dùng
  "recommendation_method": "content-based"  // Chỉ dùng content-based
}
```

### Sau Khi Train (Có `cf_model.pkl`)

```javascript
// User request tour (same)
POST /api/v1/tours/recommend
{
  "user_profile": {
    "user_id": 1,  // ← User có history
    ...
  }
}

// Backend response
{
  "destinations": [...],
  "cf_used": true,  // ✅ CF được dùng!
  "recommendation_method": "hybrid",  // CF + Content-based
  "cf_score_boost": 0.3,  // CF ảnh hưởng 30% đến scoring
  "similar_users": [2, 5, 7],  // Users giống với user 1
  "cf_recommendations": [
    {
      "destination_id": 15,
      "predicted_rating": 4.8,
      "reason": "Users similar to you loved this place"
    }
  ]
}
```

---

## 📊 Model File Structure

Khi train xong, `cf_model.pkl` sẽ chứa:

```python
{
  "user_item_matrix": np.ndarray,      # User-Item interaction matrix
  "user_similarity": np.ndarray,       # User-User similarity matrix
  "item_similarity": np.ndarray,       # Item-Item similarity matrix
  "user_ids": [1, 2, 3, ...],          # List of user IDs
  "dest_ids": [1, 2, 3, ...],          # List of destination IDs
  "trained_at": "2025-11-20T15:30:00", # Training timestamp
  "n_users": 5,                         # Number of users
  "n_destinations": 50,                 # Number of destinations
  "n_ratings": 35                       # Number of ratings
}
```

---

## ❓ FAQs

### Q: Tại sao chưa có `cf_model.pkl`?
**A**: Model chưa được train. Cần đủ dữ liệu (5+ users, 30+ ratings) rồi chạy `python train_cf_model.py`.

### Q: CF có hoạt động không nếu không có model?
**A**: KHÔNG. Hệ thống sẽ tự động fallback về Content-based filtering.

### Q: Tôi đã có ratings, sao chưa có recommendations?
**A**: Ratings được lưu vào DB, nhưng phải train model mới có CF recommendations. Chạy `train_cf_model.py`.

### Q: Train model mất bao lâu?
**A**: Với 5-10 users và 30-50 ratings: < 1 giây. Với 1000+ users: vài giây.

### Q: Model lưu ở đâu?
**A**: `d:\Hackathon\backend\cf_model.pkl`

### Q: Có cần retrain không?
**A**: CÓ. Nên retrain mỗi ngày/tuần khi có dữ liệu mới để cải thiện accuracy.

---

## 🎓 Summary

```
📍 Bạn đang ở đây:
   ✅ APIs đang hoạt động (ratings/favorites/visits)
   ✅ Đang thu thập dữ liệu
   ❌ Model chưa train
   ❌ CF chưa hoạt động

📝 Cần làm:
   1. Thu thập đủ dữ liệu (5+ users, 30+ ratings)
   2. Chạy: python check_cf_status.py (check)
   3. Chạy: python train_cf_model.py (train)
   4. Restart server
   5. CF sẽ tự động được dùng trong recommendations

🎯 Kết quả:
   ✅ cf_model.pkl được tạo ra
   ✅ CF recommendations hoạt động
   ✅ Tours được personalized theo user history
```

---

## 📞 Need Help?

1. Check status: `python check_cf_status.py`
2. View logs: Check console output khi train
3. Test model: Sau khi train, gọi `/api/v1/tours/recommend` với `user_id`

---

**Chúc bạn train model thành công! 🎉**

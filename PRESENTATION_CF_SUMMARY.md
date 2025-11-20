# 🎯 COLLABORATIVE FILTERING - TÓM TẮT THUYẾT TRÌNH

## 1️⃣ PAIN POINT (Vấn đề)

### ❌ Hệ thống hiện tại
- Chỉ dựa vào **quiz/profile ban đầu**
- **Không học** từ hành vi thực tế
- Mọi user cùng profile → **cùng recommendation**
- **Không tận dụng** dữ liệu từ users khác

### 💡 Ví dụ
```
User A chọn "Beach" → Recommend: Mỹ Khê, Sơn Trà
User B chọn "Beach" → Recommend: Mỹ Khê, Sơn Trà (y hệt!)

Thực tế:
- A thích biển + ăn uống → nên có quán ăn
- B thích biển + chụp ảnh → nên có sunset spots
```

---

## 2️⃣ GIẢI PHÁP

### 🎯 Collaborative Filtering (CF)
> **"Học từ cộng đồng - Recommend dựa trên similar users"**

### Cách hoạt động
```
User A và User B giống nhau (cùng rate nhiều địa điểm)
    ↓
User B thích địa điểm X mà User A chưa đi
    ↓
→ Recommend X cho User A (predicted rating: 4.8⭐)
```

### Hybrid Approach
```
Final Score = Content-Based (70%) + CF (30%)
            = Quiz/Profile      + User History
```

---

## 3️⃣ IMPLEMENTATION

### ✅ Đã Hoàn Thành

#### A. Thu Thập Dữ Liệu
**4 Public APIs (không cần auth):**
```javascript
POST /api/v1/ratings/    // Đánh giá địa điểm
POST /api/v1/favorites/  // Lưu yêu thích
POST /api/v1/visits/     // Check-in
POST /api/v1/feedback/   // Track hành vi (click, view, skip)
```

#### B. CF Service
- Build User-Item matrix
- Calculate similarity (cosine)
- Predict ratings cho destinations chưa visit

#### C. Training Pipeline
```bash
python check_cf_status.py   # Check đủ dữ liệu chưa
python train_cf_model.py    # Train model
```

#### D. Hybrid Recommendation
```python
if (user_có_history && cf_model_ready):
    scores = CF(30%) + Content-Based(70%)
else:
    scores = Content-Based(100%)  # Fallback
```

---

## 4️⃣ DEMO FLOW

### Scenario: 3 Users ở Đà Nẵng

```
📱 User 1 (John):
   - Rate: Mỹ Khê (5⭐), Sơn Trà (4.5⭐)
   - Request tour → Content-based (chưa đủ CF data)

📱 User 2 (Mary):
   - Rate: Mỹ Khê (5⭐), Sơn Trà (4⭐), Hội An (5⭐)

📱 User 3, 4, 5... (more users)

🧠 Backend:
   - Đủ data → Train model → cf_model.pkl

📱 User 1 (John) - Request lần 2:
   - CF detect: John ≈ Mary (90% similar)
   - Mary thích Hội An → Recommend cho John
   - Result: Personalized tour với Hội An! ✨
```

---

## 5️⃣ TECHNICAL DETAILS

### Requirements
| Metric | Minimum | Optimal |
|--------|---------|---------|
| Users | ≥ 5 | 50+ |
| Ratings | ≥ 30 | 500+ |
| Common destinations | ≥ 3 | 10+ |

### Tech Stack
- **Algorithm**: Cosine Similarity + Matrix Factorization
- **Libraries**: NumPy, Scikit-learn, SciPy
- **Storage**: PostgreSQL + Pickle (model)
- **APIs**: FastAPI (4 public endpoints)

### Fallback Mechanism
```
Request → Check CF ready?
            ↓ NO
         Content-Based (fallback)
            ↓ YES
         Hybrid (CF + CB)
```

---

## 6️⃣ RESULTS

### ✅ Achievements
- 4 Public APIs hoạt động ổn định
- CF Service implementation hoàn chỉnh
- Training scripts sẵn sàng
- Hybrid recommendation với auto fallback
- Documentation đầy đủ

### 🎯 Impact
- **Cá nhân hóa** dựa trên user history
- **Học từ cộng đồng** (similar users)
- **Accuracy tăng** theo thời gian
- **Zero downtime** (auto fallback)

---

## 7️⃣ NEXT STEPS

### Ngắn hạn
- Thu thập data từ users thực
- Train model đầu tiên
- A/B testing: CB vs Hybrid

### Dài hạn
- Neural Collaborative Filtering (Deep Learning)
- Real-time model updates
- Seasonal trends & time decay

---

## 🎤 KEY TALKING POINTS

### Mở đầu (30s)
*"Hệ thống hiện tại không học từ hành vi thực tế. CF giúp cá nhân hóa bằng cách học từ similar users."*

### Pain Point (1 min)
*"2 users cùng chọn 'Beach' nhưng sở thích khác nhau. Không tận dụng được data từ cộng đồng."*

### Solution (1.5 min)
*"CF = Học từ cộng đồng. Nếu A giống B và B thích X → Recommend X cho A. Kết hợp CB để có Hybrid."*

### Demo (2 min)
*"4 APIs thu thập data. Train model khi đủ users. Tự động fallback nếu chưa ready."*

### Kết (30s)
*"Infrastructure hoàn chỉnh. Đang thu thập data. Sẵn sàng scale khi có users."*

---

## 📊 QUICK STATS

```
✅ 4 APIs          → Thu thập ratings/favorites/visits/feedback
✅ 1 Service       → Collaborative Filtering logic
✅ 2 Scripts       → Check status + Train model
✅ Hybrid System   → CF (30%) + CB (70%)
✅ Auto Fallback   → Zero downtime
✅ 4 Docs          → Đầy đủ documentation
```

---

## 💡 ONE-LINER

**"Collaborative Filtering giúp hệ thống học từ hành vi thực tế của cộng đồng để cá nhân hóa recommendations, tự động fallback về Content-Based khi chưa đủ dữ liệu."**

---

**Good luck với presentation! 🚀**

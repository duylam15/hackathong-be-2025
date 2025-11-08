# 🏷️ TAGS API - HƯỚNG DẪN CHO FRONTEND

## 📋 TỔNG QUAN

API Tags cung cấp **30 tags** được phân thành **3 categories** để người dùng chọn preferences khi gợi ý tour.

### 🎯 MỤC ĐÍCH
- FE lấy danh sách tags từ API
- Hiển thị cho user chọn (checkbox/chip UI)
- Gửi danh sách tags đã chọn vào API tour recommendation

---

## 📊 CẤU TRÚC TAGS

### **3 Categories:**

1. **INTEREST** (Sở thích) - 12 tags
   - Những gì người dùng quan tâm: lịch sử, văn hóa, ẩm thực...

2. **ACTIVITY** (Hoạt động) - 10 tags
   - Những gì người dùng muốn làm: chụp ảnh, mua sắm, leo núi...

3. **ATMOSPHERE** (Không khí) - 8 tags
   - Bầu không khí mong muốn: thư giãn, phiêu lưu, gia đình...

---

## 🔌 API ENDPOINTS

### 1. **GET /api/v1/tags/** - Lấy tất cả tags

```bash
curl "http://localhost:8000/api/v1/tags/"
```

**Response:**
```json
{
  "tags": [
    {
      "tag_id": 1,
      "tag_name": "history",
      "tag_display_name": "Lịch sử",
      "tag_category": "interest",
      "description": "Địa điểm lịch sử, di tích văn hóa",
      "icon": "🏛️",
      "created_date": "2025-11-08T10:00:00",
      "updated_date": "2025-11-08T10:00:00",
      "is_active": true
    },
    // ... 29 tags khác
  ],
  "total": 30,
  "categories": ["interest", "activity", "atmosphere"]
}
```

### 2. **GET /api/v1/tags/?category=interest** - Lấy tags theo category

```bash
# Lấy tags Interest (Sở thích)
curl "http://localhost:8000/api/v1/tags/?category=interest"

# Lấy tags Activity (Hoạt động)
curl "http://localhost:8000/api/v1/tags/?category=activity"

# Lấy tags Atmosphere (Không khí)
curl "http://localhost:8000/api/v1/tags/?category=atmosphere"
```

---

## 💡 CÁCH SỬ DỤNG TRONG FE

### **Bước 1: Lấy tags khi load trang**

```javascript
// React/Vue/Angular example
const fetchTags = async () => {
  const response = await fetch('http://localhost:8000/api/v1/tags/');
  const data = await response.json();
  
  // Group tags by category
  const tagsByCategory = {
    interest: data.tags.filter(t => t.tag_category === 'interest'),
    activity: data.tags.filter(t => t.tag_category === 'activity'),
    atmosphere: data.tags.filter(t => t.tag_category === 'atmosphere')
  };
  
  return tagsByCategory;
};
```

### **Bước 2: Hiển thị UI cho user chọn**

**Gợi ý UI: Chips/Pills với Icon**

```jsx
// React example
<div className="tag-selection">
  <h3>🎯 Sở thích của bạn (Interest)</h3>
  <div className="tags-grid">
    {interestTags.map(tag => (
      <Chip
        key={tag.tag_id}
        icon={tag.icon}
        label={tag.tag_display_name}
        selected={selectedTags.includes(tag.tag_name)}
        onClick={() => toggleTag(tag.tag_name)}
      />
    ))}
  </div>
  
  <h3>🏃 Hoạt động yêu thích (Activity)</h3>
  <div className="tags-grid">
    {activityTags.map(tag => (
      <Chip
        key={tag.tag_id}
        icon={tag.icon}
        label={tag.tag_display_name}
        selected={selectedTags.includes(tag.tag_name)}
        onClick={() => toggleTag(tag.tag_name)}
      />
    ))}
  </div>
  
  <h3>🌈 Không khí mong muốn (Atmosphere)</h3>
  <div className="tags-grid">
    {atmosphereTags.map(tag => (
      <Chip
        key={tag.tag_id}
        icon={tag.icon}
        label={tag.tag_display_name}
        selected={selectedTags.includes(tag.tag_name)}
        onClick={() => toggleTag(tag.tag_name)}
      />
    ))}
  </div>
</div>
```

### **Bước 3: Gửi preference vào API tour recommendation**

```javascript
// User đã chọn: Lịch sử, Văn hóa, Chụp ảnh, Thư giãn
const selectedTags = ['history', 'culture', 'photography', 'relaxation'];

// Gửi vào tour recommendation API
const getTourRecommendation = async () => {
  const response = await fetch('http://localhost:8000/api/v1/tours/recommend', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_profile: {
        type: 'Cultural',
        preference: selectedTags,  // 👈 GỬI TAGS ĐÃ CHỌN VÀO ĐÂY
        budget: 500000,
        time_available: 8,
        max_locations: 5
      }
    })
  });
  
  const tour = await response.json();
  return tour;
};
```

---

## 📝 DANH SÁCH 30 TAGS ĐẦY ĐỦ

### **INTEREST (Sở thích) - 12 tags**

| tag_name | tag_display_name | icon | description |
|----------|------------------|------|-------------|
| `history` | Lịch sử | 🏛️ | Địa điểm lịch sử, di tích văn hóa |
| `culture` | Văn hóa | 🎭 | Văn hóa truyền thống, phong tục tập quán |
| `architecture` | Kiến trúc | 🏗️ | Công trình kiến trúc đẹp |
| `art` | Nghệ thuật | 🎨 | Bảo tàng nghệ thuật, triển lãm |
| `museum` | Bảo tàng | 🏛️ | Bảo tàng các loại |
| `nature` | Thiên nhiên | 🌿 | Cảnh quan thiên nhiên, vườn quốc gia |
| `food` | Ẩm thực | 🍜 | Món ăn địa phương, nhà hàng |
| `street_food` | Ẩm thực đường phố | 🥘 | Món ăn vỉa hè, chợ ăn uống |
| `local` | Địa phương | 🏘️ | Trải nghiệm địa phương, dân dã |
| `religion` | Tôn giáo | ⛪ | Chùa chiền, nhà thờ |
| `education` | Giáo dục | 📚 | Học tập, tìm hiểu kiến thức |
| `landmark` | Địa danh | 📍 | Địa điểm nổi tiếng, biểu tượng |

### **ACTIVITY (Hoạt động) - 10 tags**

| tag_name | tag_display_name | icon | description |
|----------|------------------|------|-------------|
| `photography` | Chụp ảnh | 📷 | Địa điểm đẹp để chụp ảnh |
| `shopping` | Mua sắm | 🛍️ | Chợ, trung tâm thương mại |
| `hiking` | Leo núi | 🥾 | Đi bộ đường dài, leo núi |
| `outdoor` | Ngoài trời | 🏕️ | Hoạt động ngoài trời |
| `sports` | Thể thao | ⚽ | Hoạt động thể thao |
| `water_activities` | Hoạt động nước | 🏊 | Bơi lội, lặn biển |
| `entertainment` | Giải trí | 🎪 | Vui chơi giải trí |
| `nightlife` | Cuộc sống đêm | 🌃 | Bar, club, phố đêm |
| `sightseeing` | Tham quan | 👀 | Ngắm cảnh, tham quan |
| `walking` | Đi bộ | 🚶 | Dạo bộ, khám phá đi bộ |

### **ATMOSPHERE (Không khí) - 8 tags**

| tag_name | tag_display_name | icon | description |
|----------|------------------|------|-------------|
| `relaxation` | Thư giãn | 🧘 | Yên tĩnh, thư giãn |
| `adventure` | Phiêu lưu | 🧗 | Mạo hiểm, khám phá |
| `family` | Gia đình | 👨‍👩‍👧‍👦 | Phù hợp cho gia đình, trẻ em |
| `romantic` | Lãng mạn | 💑 | Phù hợp cho cặp đôi |
| `peaceful` | Yên bình | ☮️ | Không gian yên tĩnh, thanh bình |
| `vibrant` | Sôi động | 🎉 | Nhộn nhịp, sôi động |
| `luxury` | Sang trọng | 💎 | Cao cấp, xa hoa |
| `budget` | Tiết kiệm | 💰 | Giá cả phải chăng |
| `authentic` | Chân thật | ✨ | Trải nghiệm chân thật, địa phương |
| `modern` | Hiện đại | 🏙️ | Hiện đại, công nghệ cao |

---

## 🎨 GỢI Ý UI/UX

### **1. Màn hình chọn preferences**

```
┌─────────────────────────────────────┐
│  Bạn thích gì khi du lịch? 🎯       │
├─────────────────────────────────────┤
│                                     │
│  [🏛️ Lịch sử]  [🎭 Văn hóa]         │
│  [🏗️ Kiến trúc]  [🎨 Nghệ thuật]    │
│  [🌿 Thiên nhiên]  [🍜 Ẩm thực]     │
│  ...                                │
│                                     │
│  Hoạt động yêu thích? 🏃            │
│  [📷 Chụp ảnh]  [🛍️ Mua sắm]        │
│  [🥾 Leo núi]  [🏕️ Ngoài trời]      │
│  ...                                │
│                                     │
│  Không khí mong muốn? 🌈            │
│  [🧘 Thư giãn]  [🧗 Phiêu lưu]       │
│  [👨‍👩‍👧‍👦 Gia đình]  [💑 Lãng mạn]     │
│  ...                                │
│                                     │
│         [Tìm tour phù hợp] ✨       │
└─────────────────────────────────────┘
```

### **2. Chip UI State**

- **Unselected**: Nền trắng, viền xám, text đen
- **Selected**: Nền xanh (primary color), text trắng, có icon ✓
- **Hover**: Shadow nhẹ, scale lên 1.05

### **3. Best Practices**

- ✅ Hiển thị icon để dễ nhận biết
- ✅ Cho phép chọn nhiều tags (multi-select)
- ✅ Group theo category với tiêu đề rõ ràng
- ✅ Tooltip hiển thị description khi hover
- ✅ Responsive: Grid layout 2-3 cột trên mobile
- ✅ Save selected tags vào localStorage

---

## 🔄 LUỒNG HOẠT ĐỘNG

```
1. User vào app
   ↓
2. FE call GET /api/v1/tags/
   ↓
3. FE hiển thị 30 tags theo 3 categories
   ↓
4. User chọn 3-7 tags (ví dụ: history, culture, photography)
   ↓
5. User nhập budget, thời gian, số địa điểm
   ↓
6. FE gửi POST /api/v1/tours/recommend
   Body: {
     user_profile: {
       type: "Cultural",
       preference: ["history", "culture", "photography"],
       budget: 500000,
       time_available: 8,
       max_locations: 5
     }
   }
   ↓
7. BE tính điểm cho destinations dựa trên tags
   ↓
8. BE tối ưu lộ trình và trả về tour
   ↓
9. FE hiển thị lộ trình tour
```

---

## 📌 LƯU Ý QUAN TRỌNG

1. **tag_name vs tag_display_name**
   - `tag_name`: Gửi vào API (lowercase, English)
   - `tag_display_name`: Hiển thị UI (Tiếng Việt)

2. **Số lượng tags nên chọn**: 3-7 tags
   - Quá ít: Kết quả không chính xác
   - Quá nhiều: Mất focus

3. **Caching**: Cache tags response trong 1 giờ (tags ít thay đổi)

4. **Fallback**: Nếu user không chọn tags, có thể dùng tags default theo type:
   - Cultural → ["history", "culture", "architecture"]
   - Adventure → ["hiking", "outdoor", "nature"]
   - Family → ["family", "entertainment", "peaceful"]
   - etc.

---

## ✅ CHECKLIST IMPLEMENTATION

- [ ] Call API GET /api/v1/tags/ khi load app
- [ ] Parse và group tags theo category
- [ ] Tạo UI chip/button cho từng tag
- [ ] Implement multi-select logic
- [ ] Validate: yêu cầu chọn ít nhất 1 tag
- [ ] Gửi `tag_name` (không phải tag_display_name) vào API tour
- [ ] Test với nhiều combination tags khác nhau
- [ ] Add loading state khi gọi API
- [ ] Handle error nếu API tags fail

---

## 🎉 KẾT LUẬN

Tags API cung cấp nguồn dữ liệu chuẩn để:
- ✅ User chọn preferences dễ dàng với UI thân thiện
- ✅ Backend tính điểm chính xác hơn (40% trọng số!)
- ✅ Recommend tour phù hợp với sở thích cá nhân

**API Endpoint chính:** `GET /api/v1/tags/`

**Sử dụng trong tour:** `POST /api/v1/tours/recommend` với field `preference: [tag_names]`

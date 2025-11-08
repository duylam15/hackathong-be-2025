# 📸 HƯỚNG DẪN TEST API VỚI IMAGES

## ⚠️ QUAN TRỌNG: Restart server trước khi test
```bash
# Dừng server cũ (Ctrl+C)
# Chạy lại server
uvicorn app.main:app --reload
```

---

## 1️⃣ TEST GET - Xem destination có field images chưa

```bash
# Test 1: Get destination ID = 1
curl -s "http://localhost:8000/api/v1/destinations/1" | python3 -m json.tool

# Test 2: Get all destinations (search endpoint)
curl -s "http://localhost:8000/api/v1/destinations/search?page=1&page_size=3" | python3 -m json.tool
```

**Kết quả mong đợi:** Response sẽ có thêm field `"images": []` (mảng rỗng vì chưa có ảnh)

---

## 2️⃣ TEST POST - Tạo destination MỚI với images

```bash
# Tạo destination với 3 hình ảnh
curl -X POST "http://localhost:8000/api/v1/destinations/" \
  -H "Content-Type: application/json" \
  -d '{
    "destination_name": "Dinh Độc Lập",
    "destination_type": "Cultural",
    "tags": ["Lịch sử", "Kiến trúc", "Chính trị"],
    "latitude": 10.7769,
    "longitude": 106.6955,
    "location_address": "135 Nam Kỳ Khởi Nghĩa, Bến Thành, Quận 1",
    "price": 65000,
    "opening_hours": "07:30-11:00, 13:00-16:00",
    "visit_time": 90,
    "facilities": ["Bãi đỗ xe", "Wifi", "Nhà vệ sinh", "Quầy nước"],
    "images": [
      "https://example.com/dinh-doc-lap-1.jpg",
      "https://example.com/dinh-doc-lap-2.jpg",
      "https://example.com/dinh-doc-lap-3.jpg"
    ],
    "extra_info": {
      "rating": 4.7,
      "reviews": 12500,
      "highlights": ["Tòa nhà lịch sử", "Kiến trúc đẹp", "Vườn cây xanh mát"]
    }
  }' | python3 -m json.tool
```

```bash
# Tạo destination với nhiều ảnh hơn
curl -X POST "http://localhost:8000/api/v1/destinations/" \
  -H "Content-Type: application/json" \
  -d '{
    "destination_name": "Bảo Tàng Chứng Tích Chiến Tranh",
    "destination_type": "Cultural",
    "tags": ["Lịch sử", "Giáo dục", "Bảo tàng"],
    "location_address": "28 Võ Văn Tần, Phường 6, Quận 3",
    "price": 40000,
    "opening_hours": "07:30-18:00",
    "visit_time": 120,
    "images": [
      "https://example.com/war-museum-exterior.jpg",
      "https://example.com/war-museum-tank.jpg",
      "https://example.com/war-museum-exhibition-1.jpg",
      "https://example.com/war-museum-exhibition-2.jpg",
      "https://example.com/war-museum-courtyard.jpg"
    ]
  }' | python3 -m json.tool
```

---

## 3️⃣ TEST PUT - Cập nhật images

```bash
# Test 3.1: Thêm images vào destination đã tồn tại (ID = 1)
curl -X PUT "http://localhost:8000/api/v1/destinations/1" \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      "https://upload.wikimedia.org/wikipedia/commons/nha-tho-duc-ba-1.jpg",
      "https://upload.wikimedia.org/wikipedia/commons/nha-tho-duc-ba-2.jpg",
      "https://upload.wikimedia.org/wikipedia/commons/nha-tho-duc-ba-3.jpg"
    ]
  }' | python3 -m json.tool

# Test 3.2: Cập nhật thêm ảnh cho destination ID = 2
curl -X PUT "http://localhost:8000/api/v1/destinations/2" \
  -H "Content-Type: application/json" \
  -d '{
    "images": [
      "https://example.com/ben-nha-rong-exterior.jpg",
      "https://example.com/ben-nha-rong-statue.jpg"
    ]
  }' | python3 -m json.tool

# Test 3.3: Cập nhật destination + thêm images cùng lúc
curl -X PUT "http://localhost:8000/api/v1/destinations/3" \
  -H "Content-Type: application/json" \
  -d '{
    "destination_name": "Phố Đi Bộ Nguyễn Huệ - Updated",
    "price": 0,
    "images": [
      "https://example.com/nguyen-hue-night.jpg",
      "https://example.com/nguyen-hue-fountain.jpg",
      "https://example.com/nguyen-hue-crowd.jpg"
    ]
  }' | python3 -m json.tool

# Test 3.4: Xóa tất cả images (set về mảng rỗng)
curl -X PUT "http://localhost:8000/api/v1/destinations/1" \
  -H "Content-Type: application/json" \
  -d '{
    "images": []
  }' | python3 -m json.tool
```

---

## 4️⃣ TEST SEARCH - Xem images trong kết quả tìm kiếm

```bash
# Test 4.1: Search với pagination - xem tất cả có images
curl -s "http://localhost:8000/api/v1/destinations/search?page=1&page_size=5" | python3 -m json.tool

# Test 4.2: Search theo type và xem images
curl -s "http://localhost:8000/api/v1/destinations/search?destination_type=Cultural&page_size=10" | python3 -m json.tool
```

---

## 5️⃣ TEST DELETE - Soft delete vẫn giữ images

```bash
# Xóa destination và kiểm tra images vẫn còn
curl -X DELETE "http://localhost:8000/api/v1/destinations/20" -v

# Kiểm tra destination đã xóa (is_active=false) vẫn có images
curl -s "http://localhost:8000/api/v1/destinations/search?is_active=false" | python3 -m json.tool
```

---

## 📋 RESPONSE FORMAT MẪU

### GET /destinations/{id}
```json
{
  "destination_id": 1,
  "destination_name": "Nhà Thờ Đức Bà",
  "destination_type": "Cultural",
  "tags": ["Lịch sử", "Kiến trúc", "Tôn giáo"],
  "latitude": "10.77963000",
  "longitude": "106.69900000",
  "location_address": "01 Công xã Paris, Bến Nghé, Quận 1",
  "price": 0,
  "opening_hours": "08:00-11:00, 14:00-17:00",
  "visit_time": 30,
  "facilities": ["Nhà vệ sinh"],
  "extra_info": {
    "rating": 4.5,
    "reviews": 15234
  },
  "images": [
    "https://example.com/nha-tho-duc-ba-1.jpg",
    "https://example.com/nha-tho-duc-ba-2.jpg",
    "https://example.com/nha-tho-duc-ba-3.jpg"
  ],
  "created_date": "2025-11-08T12:00:00",
  "updated_date": "2025-11-08T12:30:00",
  "is_active": true
}
```

### POST /destinations/ - CREATE
```json
{
  "destination_name": "Dinh Độc Lập",
  "destination_type": "Cultural",
  "images": [
    "https://example.com/dinh-doc-lap-1.jpg",
    "https://example.com/dinh-doc-lap-2.jpg"
  ]
  // ... other fields
}
```

### PUT /destinations/{id} - UPDATE
```json
{
  "images": [
    "https://new-url.com/image1.jpg",
    "https://new-url.com/image2.jpg"
  ]
}
```

---

## 🎯 TIPS

1. **Images là mảng String**: Có thể chứa nhiều URLs
2. **Có thể rỗng**: `"images": []` là hợp lệ
3. **Update images**: Gửi mảng mới sẽ REPLACE hoàn toàn mảng cũ
4. **URLs bất kỳ**: Có thể dùng URLs từ bất kỳ nguồn nào (CDN, cloud storage, etc.)

---

## 🔗 SAMPLE IMAGE URLS (để test)

```json
[
  "https://images.unsplash.com/photo-1583417319070-4a69db38a482",
  "https://images.unsplash.com/photo-1555993539-1732b0258235",
  "https://images.unsplash.com/photo-1528127269322-539801943592",
  "https://picsum.photos/800/600?random=1",
  "https://picsum.photos/800/600?random=2"
]
```

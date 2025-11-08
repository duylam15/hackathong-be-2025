# 🗺️ Tour Optimizer - Navigation Guide

## 🚀 Bắt Đầu Nhanh

**Bạn muốn làm gì?**

### 1️⃣ Chạy ngay (1 phút)
→ Đọc [`QUICKSTART.md`](QUICKSTART.md)

### 2️⃣ Hiểu toàn bộ project
→ Đọc [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md)

### 3️⃣ Học cách sử dụng
→ Đọc [`README.md`](README.md)

### 4️⃣ Hiểu sâu thuật toán
→ Đọc [`GUIDE.md`](GUIDE.md)

---

## 📂 Files Chính

### 🔴 MỚI BẮT ĐẦU? CHẠY FILE NÀY:
```bash
python3 demo_simple.py
```
→ File dễ nhất để tùy chỉnh và chạy

### 🟢 CÁC FILE KHÁC:

| File | Khi nào dùng? |
|------|---------------|
| `tour_optimizer.py` | Xem 5 user types cùng lúc |
| `analyze_scoring.py` | Hiểu tại sao địa điểm được chọn |
| `advanced_examples.py` | Tour nhiều ngày, export, batch |

---

## 📚 Tài Liệu

| File | Độ Dài | Đối Tượng | Nội Dung |
|------|--------|-----------|----------|
| **QUICKSTART.md** | 5 phút | Mới bắt đầu | Commands cơ bản |
| **README.md** | 10 phút | User | Features, API |
| **GUIDE.md** | 30 phút | Developer | Thuật toán, FAQ |
| **PROJECT_SUMMARY.md** | 5 phút | Overview | Tổng quan toàn bộ |

---

## 🎯 Roadmap Học

### Level 1: Beginner (30 phút)
1. ✅ Đọc `QUICKSTART.md` (5 phút)
2. ✅ Cài đặt dependencies (1 phút)
3. ✅ Chạy `demo_simple.py` (2 phút)
4. ✅ Sửa user profile và chạy lại (5 phút)
5. ✅ Đọc kết quả trong `tour_result.json` (2 phút)
6. ✅ Thử các user types khác nhau (15 phút)

### Level 2: Intermediate (1 giờ)
1. ✅ Đọc `README.md` (10 phút)
2. ✅ Chạy `analyze_scoring.py` (5 phút)
3. ✅ Hiểu 7 tiêu chí scoring (10 phút)
4. ✅ Thêm 1 địa điểm mới vào JSON (10 phút)
5. ✅ Thử thay đổi budget/time (10 phút)
6. ✅ Export ra CSV/HTML (5 phút)
7. ✅ Đọc phần Algorithm trong README (10 phút)

### Level 3: Advanced (2-3 giờ)
1. ✅ Đọc `GUIDE.md` (30 phút)
2. ✅ Hiểu OR-Tools VRP (30 phút)
3. ✅ Chạy tất cả advanced examples (30 phút)
4. ✅ Thử custom weights (15 phút)
5. ✅ Implement multi-day tour (30 phút)
6. ✅ Đọc OR-Tools docs (30 phút)

### Level 4: Expert (1 ngày)
1. ✅ Đọc toàn bộ source code (2 giờ)
2. ✅ Hiểu từng module chi tiết (2 giờ)
3. ✅ Thử modify thuật toán (2 giờ)
4. ✅ Integrate Google Maps API (2 giờ)
5. ✅ Build database thực tế (2 giờ)

---

## 🔍 Tìm Thông Tin

### 🤔 Bạn muốn biết...

**"Cách cài đặt?"**
→ [`QUICKSTART.md`](QUICKSTART.md) hoặc [`README.md`](README.md)

**"Cách chạy demo?"**
→ [`QUICKSTART.md`](QUICKSTART.md)

**"Scoring algorithm hoạt động thế nào?"**
→ [`GUIDE.md`](GUIDE.md) → Section "Thuật Toán"

**"Cách thêm địa điểm mới?"**
→ [`GUIDE.md`](GUIDE.md) → Section "Tùy Chỉnh"

**"Cách thay đổi trọng số?"**
→ [`GUIDE.md`](GUIDE.md) → Section "Tùy Chỉnh" hoặc `advanced_examples.py` Example 1

**"OR-Tools là gì?"**
→ [`GUIDE.md`](GUIDE.md) → Section "Thuật Toán"

**"Tại sao không tìm thấy lộ trình?"**
→ [`GUIDE.md`](GUIDE.md) → Section "FAQ"

**"Cách làm tour nhiều ngày?"**
→ `advanced_examples.py` → Example 3

**"Tổng quan toàn bộ project?"**
→ [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md)

**"API reference?"**
→ [`README.md`](README.md) hoặc [`GUIDE.md`](GUIDE.md)

---

## 🎓 Tài Nguyên Bên Ngoài

### OR-Tools
- [Official Docs](https://developers.google.com/optimization)
- [VRP Guide](https://developers.google.com/optimization/routing/vrp)
- [Python Examples](https://github.com/google/or-tools/tree/stable/examples/python)

### Algorithms
- [Vehicle Routing Problem](https://en.wikipedia.org/wiki/Vehicle_routing_problem)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)
- [Local Search](https://en.wikipedia.org/wiki/Local_search_(optimization))

---

## 💡 Tips

### ✅ DOs
- ✅ Bắt đầu với `demo_simple.py`
- ✅ Đọc QUICKSTART trước
- ✅ Test với data mẫu trước khi custom
- ✅ Đọc error messages kỹ
- ✅ Backup trước khi modify

### ❌ DON'Ts
- ❌ Bỏ qua documentation
- ❌ Modify `tour_optimizer.py` nếu mới bắt đầu
- ❌ Dùng data không hợp lệ
- ❌ Set budget = 0 hoặc time = 0
- ❌ Quên activate Python environment

---

## 📞 Support

### Gặp lỗi?
1. Đọc error message
2. Check [`GUIDE.md`](GUIDE.md) FAQ section
3. Verify input data format
4. Test với demo data trước

### Cần mở rộng?
1. Đọc [`GUIDE.md`](GUIDE.md) Customization
2. Xem `advanced_examples.py`
3. Check OR-Tools docs

---

## 🎯 Quick Commands

```bash
# Setup
pip install -r requirements.txt

# Demo đơn giản (KHUYÊN DÙNG)
python3 demo_simple.py

# Demo 5 users
python3 tour_optimizer.py

# Phân tích scoring
python3 analyze_scoring.py

# Advanced examples
python3 advanced_examples.py
```

---

**Chúc bạn code vui vẻ! 🚀**

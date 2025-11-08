# 🧪 QUICK TEST - Tags API

## Test 1: Lấy tất cả tags

```bash
curl -s "http://localhost:8000/api/v1/tags/" | python3 -m json.tool | head -50
```

## Test 2: Lấy tags theo category

```bash
# Interest tags
curl -s "http://localhost:8000/api/v1/tags/?category=interest" | python3 -m json.tool

# Activity tags
curl -s "http://localhost:8000/api/v1/tags/?category=activity" | python3 -m json.tool

# Atmosphere tags
curl -s "http://localhost:8000/api/v1/tags/?category=atmosphere" | python3 -m json.tool
```

## Test 3: Test với Tour Recommendation API

```bash
# Gửi tour request với preferences từ tags
curl -X POST "http://localhost:8000/api/v1/tours/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "type": "Cultural",
      "preference": ["history", "culture", "architecture", "photography"],
      "budget": 500000,
      "time_available": 8,
      "max_locations": 5
    }
  }' | python3 -m json.tool
```

## Test 4: Verify images trong tour response

```bash
# Check xem tour trả về có images không
curl -X POST "http://localhost:8000/api/v1/tours/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "user_profile": {
      "type": "Cultural",
      "preference": ["history", "culture"],
      "budget": 300000,
      "time_available": 6,
      "max_locations": 3
    }
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print('✅ SUCCESS' if data.get('success') else '❌ FAIL'); print(f\"Locations: {data.get('total_locations', 0)}\"); route=data.get('route',[]); print(f\"First location has {len(route[0].get('images',[]))} images\" if route else 'No route')"
```

# Public API Guide - Collaborative Filtering Endpoints

## Overview

All Collaborative Filtering API endpoints are **PUBLIC** and **DO NOT require authentication**. This allows frontend to easily collect user behavior data without complex authentication flows.

## Important Changes

### ✅ What Changed
- **Removed Authentication**: All CF endpoints (`/api/v1/ratings`, `/api/v1/favorites`, `/api/v1/visits`, `/api/v1/feedback`) are now public
- **Added user_id field**: All request bodies now require `user_id` field
- **Simplified Endpoints**: Removed `/me` endpoints, replaced with `/user/{user_id}` patterns

### ⚠️ Security Considerations
- Frontend should validate `user_id` before sending requests
- Consider implementing rate limiting on server side
- Monitor for abuse patterns
- Plan to add authentication in production environment

---

## API Endpoints Reference

### 1. RATINGS API

#### Create or Update Rating
```http
POST /api/v1/ratings/
Content-Type: application/json

{
  "user_id": 1,
  "destination_id": 5,
  "rating": 4.5,
  "review_text": "Amazing place!",
  "visit_date": "2025-11-15T10:00:00"
}
```

**Response (201 Created)**:
```json
{
  "rating_id": 123,
  "user_id": 1,
  "destination_id": 5,
  "rating": 4.5,
  "review_text": "Amazing place!",
  "visit_date": "2025-11-15T10:00:00",
  "created_date": "2025-11-18T08:30:00",
  "updated_date": "2025-11-18T08:30:00"
}
```

#### Get User's Ratings
```http
GET /api/v1/ratings/user/1?skip=0&limit=100
```

**Response (200 OK)**:
```json
[
  {
    "rating_id": 123,
    "user_id": 1,
    "destination_id": 5,
    "rating": 4.5,
    "review_text": "Amazing place!",
    "visit_date": "2025-11-15T10:00:00",
    "created_date": "2025-11-18T08:30:00",
    "updated_date": "2025-11-18T08:30:00"
  }
]
```

#### Get Destination Ratings
```http
GET /api/v1/ratings/destination/5?skip=0&limit=100
```

#### Delete Rating
```http
DELETE /api/v1/ratings/{user_id}/{destination_id}
```

**Example**:
```http
DELETE /api/v1/ratings/1/5
```

**Response (204 No Content)**

---

### 2. FAVORITES API

#### Add to Favorites
```http
POST /api/v1/favorites/
Content-Type: application/json

{
  "user_id": 1,
  "destination_id": 7,
  "notes": "Want to visit in spring"
}
```

**Response (201 Created)**:
```json
{
  "favorite_id": 456,
  "user_id": 1,
  "destination_id": 7,
  "notes": "Want to visit in spring",
  "created_date": "2025-11-18T09:00:00"
}
```

#### Get User's Favorites
```http
GET /api/v1/favorites/user/1?skip=0&limit=100
```

#### Remove from Favorites
```http
DELETE /api/v1/favorites/{user_id}/{destination_id}
```

**Example**:
```http
DELETE /api/v1/favorites/1/7
```

---

### 3. VISITS API

#### Log a Visit
```http
POST /api/v1/visits/
Content-Type: application/json

{
  "user_id": 1,
  "destination_id": 3,
  "visit_date": "2025-11-18T14:30:00",
  "duration_minutes": 120,
  "completed": true
}
```

**Response (201 Created)**:
```json
{
  "log_id": 789,
  "user_id": 1,
  "destination_id": 3,
  "visit_date": "2025-11-18T14:30:00",
  "duration_minutes": 120,
  "completed": true,
  "created_date": "2025-11-18T16:30:00"
}
```

#### Get User's Visit History
```http
GET /api/v1/visits/user/1?skip=0&limit=100
```

---

### 4. FEEDBACK API

#### Track User Interaction
```http
POST /api/v1/feedback/
Content-Type: application/json

{
  "user_id": 1,
  "destination_id": 10,
  "action": "click",
  "context": {
    "source": "recommendation",
    "position": 2,
    "tour_id": 123
  }
}
```

**Allowed Actions**:
- `click` - User clicked on destination
- `skip` - User skipped destination
- `save` - User saved destination
- `share` - User shared destination
- `view_details` - User viewed destination details

**Response (201 Created)**:
```json
{
  "feedback_id": 999,
  "user_id": 1,
  "destination_id": 10,
  "action": "click",
  "context": {
    "source": "recommendation",
    "position": 2,
    "tour_id": 123
  },
  "created_date": "2025-11-18T17:00:00"
}
```

#### Get User's Feedback History
```http
GET /api/v1/feedback/user/1?skip=0&limit=100
```

---

## Frontend Integration Examples

### JavaScript/TypeScript

```typescript
// API Client Service
class CollaborativeFilteringAPI {
  private baseURL = 'http://localhost:8000/api/v1';
  
  // Rate a destination
  async rateDestination(userId: number, destinationId: number, rating: number, reviewText?: string) {
    const response = await fetch(`${this.baseURL}/ratings/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        destination_id: destinationId,
        rating: rating,
        review_text: reviewText
      })
    });
    return response.json();
  }
  
  // Add to favorites
  async addFavorite(userId: number, destinationId: number, notes?: string) {
    const response = await fetch(`${this.baseURL}/favorites/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        destination_id: destinationId,
        notes: notes
      })
    });
    return response.json();
  }
  
  // Log visit
  async logVisit(userId: number, destinationId: number, visitDate: Date, durationMinutes?: number) {
    const response = await fetch(`${this.baseURL}/visits/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        destination_id: destinationId,
        visit_date: visitDate.toISOString(),
        duration_minutes: durationMinutes,
        completed: true
      })
    });
    return response.json();
  }
  
  // Track feedback
  async trackFeedback(userId: number, destinationId: number, action: string, context?: any) {
    const response = await fetch(`${this.baseURL}/feedback/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userId,
        destination_id: destinationId,
        action: action,
        context: context
      })
    });
    return response.json();
  }
  
  // Get user ratings
  async getUserRatings(userId: number) {
    const response = await fetch(`${this.baseURL}/ratings/user/${userId}`);
    return response.json();
  }
  
  // Get user favorites
  async getUserFavorites(userId: number) {
    const response = await fetch(`${this.baseURL}/favorites/user/${userId}`);
    return response.json();
  }
}

// Usage Example
const cfAPI = new CollaborativeFilteringAPI();

// When user rates a destination
await cfAPI.rateDestination(1, 5, 4.5, "Great place!");

// When user clicks favorite button
await cfAPI.addFavorite(1, 7, "Want to visit in spring");

// When user clicks on destination card
await cfAPI.trackFeedback(1, 10, 'click', {
  source: 'recommendation',
  position: 2
});
```

### React Hooks Example

```typescript
// useFavorites.ts
import { useState, useEffect } from 'react';

export function useFavorites(userId: number) {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const loadFavorites = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/favorites/user/${userId}`);
      const data = await response.json();
      setFavorites(data);
    } catch (error) {
      console.error('Failed to load favorites:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const addFavorite = async (destinationId: number, notes?: string) => {
    try {
      const response = await fetch('/api/v1/favorites/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          destination_id: destinationId,
          notes: notes
        })
      });
      const newFavorite = await response.json();
      setFavorites([...favorites, newFavorite]);
      return newFavorite;
    } catch (error) {
      console.error('Failed to add favorite:', error);
      throw error;
    }
  };
  
  const removeFavorite = async (destinationId: number) => {
    try {
      await fetch(`/api/v1/favorites/${userId}/${destinationId}`, {
        method: 'DELETE'
      });
      setFavorites(favorites.filter(f => f.destination_id !== destinationId));
    } catch (error) {
      console.error('Failed to remove favorite:', error);
      throw error;
    }
  };
  
  useEffect(() => {
    if (userId) {
      loadFavorites();
    }
  }, [userId]);
  
  return { favorites, loading, addFavorite, removeFavorite, reload: loadFavorites };
}

// Usage in Component
function DestinationCard({ destination, userId }) {
  const { favorites, addFavorite, removeFavorite } = useFavorites(userId);
  const isFavorited = favorites.some(f => f.destination_id === destination.id);
  
  const handleToggleFavorite = async () => {
    if (isFavorited) {
      await removeFavorite(destination.id);
    } else {
      await addFavorite(destination.id);
    }
  };
  
  return (
    <div>
      <h3>{destination.name}</h3>
      <button onClick={handleToggleFavorite}>
        {isFavorited ? '❤️ Favorited' : '🤍 Add to Favorites'}
      </button>
    </div>
  );
}
```

---

## Best Practices

### 1. **Track Everything**
```typescript
// Track all user interactions for better recommendations
trackFeedback(userId, destinationId, 'click', { source: 'search' });
trackFeedback(userId, destinationId, 'view_details', { duration: 30 });
trackFeedback(userId, destinationId, 'skip', { reason: 'not_interested' });
```

### 2. **Batch Requests**
```typescript
// If user rates multiple destinations at once
const ratings = [
  { user_id: 1, destination_id: 1, rating: 4.0 },
  { user_id: 1, destination_id: 2, rating: 5.0 },
  { user_id: 1, destination_id: 3, rating: 3.5 }
];

await Promise.all(
  ratings.map(r => fetch('/api/v1/ratings/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(r)
  }))
);
```

### 3. **Error Handling**
```typescript
async function safeTrackFeedback(userId, destinationId, action) {
  try {
    await trackFeedback(userId, destinationId, action);
  } catch (error) {
    // Log to error tracking service
    console.error('Failed to track feedback:', error);
    // Don't block UI - tracking is optional
  }
}
```

### 4. **Offline Support**
```typescript
// Queue feedback when offline
const feedbackQueue = [];

async function trackFeedbackWithOfflineSupport(userId, destinationId, action) {
  const feedback = { user_id: userId, destination_id: destinationId, action };
  
  if (!navigator.onLine) {
    feedbackQueue.push(feedback);
    return;
  }
  
  try {
    await fetch('/api/v1/feedback/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(feedback)
    });
  } catch (error) {
    feedbackQueue.push(feedback);
  }
}

// Flush queue when back online
window.addEventListener('online', async () => {
  while (feedbackQueue.length > 0) {
    const feedback = feedbackQueue.shift();
    try {
      await fetch('/api/v1/feedback/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedback)
      });
    } catch (error) {
      feedbackQueue.unshift(feedback);
      break;
    }
  }
});
```

---

## Testing the API

### Using cURL

```bash
# Create rating
curl -X POST "http://localhost:8000/api/v1/ratings/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "destination_id": 5, "rating": 4.5, "review_text": "Great!"}'

# Get user ratings
curl "http://localhost:8000/api/v1/ratings/user/1"

# Add favorite
curl -X POST "http://localhost:8000/api/v1/favorites/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "destination_id": 7, "notes": "Visit in spring"}'

# Log visit
curl -X POST "http://localhost:8000/api/v1/visits/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "destination_id": 3, "visit_date": "2025-11-18T14:30:00", "duration_minutes": 120, "completed": true}'

# Track feedback
curl -X POST "http://localhost:8000/api/v1/feedback/" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "destination_id": 10, "action": "click", "context": {"source": "recommendation"}}'
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Rate destination
response = requests.post(f"{BASE_URL}/ratings/", json={
    "user_id": 1,
    "destination_id": 5,
    "rating": 4.5,
    "review_text": "Amazing place!"
})
print(response.json())

# Get user ratings
response = requests.get(f"{BASE_URL}/ratings/user/1")
print(response.json())

# Add favorite
response = requests.post(f"{BASE_URL}/favorites/", json={
    "user_id": 1,
    "destination_id": 7,
    "notes": "Want to visit in spring"
})
print(response.json())
```

---

## Migration from Authenticated to Public

If you had previously implemented authenticated endpoints:

### Old (Authenticated)
```typescript
// Required Authorization header
const response = await fetch('/api/v1/ratings/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}` // ❌ No longer needed
  },
  body: JSON.stringify({
    destination_id: 5,
    rating: 4.5
  })
});
```

### New (Public)
```typescript
// No Authorization header, user_id in body
const response = await fetch('/api/v1/ratings/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: 1,           // ✅ Add user_id
    destination_id: 5,
    rating: 4.5
  })
});
```

### Endpoint Changes

| Old Endpoint | New Endpoint | Change |
|--------------|--------------|--------|
| `POST /ratings/` (body without user_id) | `POST /ratings/` (body with user_id) | Add user_id to body |
| `GET /ratings/me` | `GET /ratings/user/{user_id}` | Use user_id in path |
| `DELETE /ratings/{destination_id}` | `DELETE /ratings/{user_id}/{destination_id}` | Add user_id to path |
| `POST /favorites/` | `POST /favorites/` (body with user_id) | Add user_id to body |
| `GET /favorites/me` | `GET /favorites/user/{user_id}` | Use user_id in path |
| `DELETE /favorites/{destination_id}` | `DELETE /favorites/{user_id}/{destination_id}` | Add user_id to path |

---

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both interfaces provide interactive API documentation and testing.

---

## Next Steps

1. ✅ **Test API endpoints** using Swagger UI or cURL
2. ✅ **Integrate into frontend** using the examples above
3. 🔄 **Collect user data** to train collaborative filtering model
4. 📊 **Monitor performance** and user engagement
5. 🔒 **Plan authentication** for production environment

---

## Support

For questions or issues:
- Check `/docs` endpoint for API documentation
- Review `COLLABORATIVE_FILTERING_GUIDE.md` for technical details
- Test endpoints using Swagger UI at `/docs`

---

## Troubleshooting

### "Provisional headers are shown" Error

If you see this warning in Chrome DevTools, it usually means:

#### 🔴 Problem: CORS Issue (Most Common)
The browser blocked the request due to CORS policy.

**Solution:**
1. Make sure backend CORS is configured correctly (already done in `app/main.py`)
2. Check if backend server is running: `http://localhost:8000`
3. Try accessing the API directly in browser to verify it works

**Test CORS:**
```bash
# Test from command line
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/api/v1/ratings/
```

#### 🔴 Problem: Backend Not Running
The request failed because the server is not responding.

**Solution:**
```bash
# Start the backend server
cd d:\Hackathon\backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 🔴 Problem: Browser Extension Blocking
Ad blockers or security extensions may block requests.

**Solution:**
- Disable browser extensions temporarily
- Try in incognito/private mode
- Whitelist `localhost` in your ad blocker

#### 🔴 Problem: Wrong URL
Request URL is incorrect or has typos.

**Solution:**
```javascript
// ❌ Wrong
fetch('http://localhost:8000/ratings/')  // Missing /api/v1

// ✅ Correct
fetch('http://localhost:8000/api/v1/ratings/')
```

#### 🔴 Problem: Network Error
Request is being cancelled before completion.

**Solution:**
```javascript
// Add error handling
async function createRating(data) {
  try {
    const response = await fetch('http://localhost:8000/api/v1/ratings/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      console.error('HTTP Error:', response.status, response.statusText);
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Network Error:', error);
    throw error;
  }
}
```

### How to Debug CORS Issues

#### 1. Check Browser Console
Look for CORS error messages:
```
Access to fetch at 'http://localhost:8000/api/v1/ratings/' from origin 
'http://localhost:5173' has been blocked by CORS policy
```

#### 2. Check Network Tab
- Go to Chrome DevTools → Network tab
- Click on the failed request
- Check "Response Headers" for CORS headers:
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: *`
  - `Access-Control-Allow-Headers: *`

#### 3. Test with cURL
```bash
# Test if API works directly
curl http://localhost:8000/api/v1/ratings/user/1

# Test CORS preflight
curl -X OPTIONS http://localhost:8000/api/v1/ratings/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

#### 4. Verify Backend CORS Configuration
Check `app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # ✅ Should be "*" for development
    allow_credentials=True,
    allow_methods=["*"],       # ✅ Should allow all methods
    allow_headers=["*"],       # ✅ Should allow all headers
    expose_headers=["*"],      # ✅ Should expose all headers
)
```

### Common Frontend Issues

#### Issue: Fetch fails silently
```javascript
// ❌ Bad: No error handling
fetch('/api/v1/ratings/', { method: 'POST', body: data });

// ✅ Good: Proper error handling
fetch('/api/v1/ratings/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
.then(response => {
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
})
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

#### Issue: Wrong Content-Type
```javascript
// ❌ Missing Content-Type
fetch('/api/v1/ratings/', {
  method: 'POST',
  body: JSON.stringify(data)  // Backend won't parse this correctly
});

// ✅ Include Content-Type header
fetch('/api/v1/ratings/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },  // ✅ Required!
  body: JSON.stringify(data)
});
```

#### Issue: Incorrect JSON format
```javascript
// ❌ Sending form data instead of JSON
const formData = new FormData();
formData.append('user_id', 1);

// ✅ Send JSON object
const data = {
  user_id: 1,
  destination_id: 5,
  rating: 4.5
};
fetch('/api/v1/ratings/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
});
```

### Testing Checklist

Before reporting issues, verify:

- [ ] Backend server is running (`http://localhost:8000`)
- [ ] Can access `/docs` endpoint (`http://localhost:8000/docs`)
- [ ] API works in Swagger UI
- [ ] Using correct URL with `/api/v1` prefix
- [ ] Request includes `Content-Type: application/json` header
- [ ] Request body is valid JSON
- [ ] Browser console shows no CORS errors
- [ ] No browser extensions blocking requests
- [ ] Request body includes required `user_id` field

### Quick Fix Commands

```bash
# Restart backend server
cd d:\Hackathon\backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Test API is working
curl http://localhost:8000/health

# Test specific endpoint
curl http://localhost:8000/api/v1/ratings/user/1

# Test POST request
curl -X POST http://localhost:8000/api/v1/ratings/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"destination_id":5,"rating":4.5}'
```

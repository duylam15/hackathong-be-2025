# 📊 SƠ ĐỒ LUỒNG COLLABORATIVE FILTERING

## Sơ Đồ 1: Tổng Quan Hệ Thống

```mermaid
flowchart TB
    subgraph Frontend["🖥️ FRONTEND"]
        U1[User A]
        U2[User B]
        U3[User C]
    end
    
    subgraph APIs["📡 PUBLIC APIs"]
        API1[POST /ratings/]
        API2[POST /favorites/]
        API3[POST /visits/]
        API4[POST /feedback/]
    end
    
    subgraph Database["💾 DATABASE"]
        DB1[(destination_ratings)]
        DB2[(user_favorites)]
        DB3[(visit_logs)]
        DB4[(user_feedback)]
    end
    
    subgraph Training["🧠 TRAINING"]
        T1[Check Status]
        T2[Build Matrix]
        T3[Calculate Similarity]
        T4[Save Model]
        MODEL[cf_model.pkl]
    end
    
    subgraph Recommendation["🎯 RECOMMENDATION"]
        R1{User có history?}
        R2{CF Model ready?}
        CF[Collaborative Filtering]
        CB[Content-Based]
        HYBRID[Hybrid Scoring]
        TOUR[Personalized Tour]
    end
    
    U1 --> API1
    U2 --> API2
    U3 --> API3
    
    API1 --> DB1
    API2 --> DB2
    API3 --> DB3
    API4 --> DB4
    
    DB1 --> T1
    DB2 --> T1
    DB3 --> T1
    T1 -->|Đủ data| T2
    T2 --> T3
    T3 --> T4
    T4 --> MODEL
    
    U1 -->|Request Tour| R1
    R1 -->|Yes| R2
    R1 -->|No| CB
    R2 -->|Yes| CF
    R2 -->|No| CB
    CF --> HYBRID
    CB --> HYBRID
    HYBRID --> TOUR
    
    style Frontend fill:#e1f5ff
    style APIs fill:#fff4e1
    style Database fill:#f0e1ff
    style Training fill:#ffe1f5
    style Recommendation fill:#e1ffe1
    style MODEL fill:#ffd700
```

---

## Sơ Đồ 2: Luồng Thu Thập Dữ Liệu

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant FE as 🖥️ Frontend
    participant API as 📡 Backend API
    participant DB as 💾 Database
    
    U->>FE: 1. Đăng nhập
    FE->>API: POST /login
    API->>FE: user_id, token
    
    U->>FE: 2. Xem destination
    U->>FE: 3. Click "Rate"
    FE->>API: POST /ratings/<br/>{user_id, destination_id, rating}
    API->>DB: Save rating
    DB->>API: ✅ Success
    API->>FE: Rating saved
    
    U->>FE: 4. Click "Favorite"
    FE->>API: POST /favorites/<br/>{user_id, destination_id}
    API->>DB: Save favorite
    DB->>API: ✅ Success
    API->>FE: Favorite saved
    
    U->>FE: 5. Check-in tại địa điểm
    FE->>API: POST /visits/<br/>{user_id, destination_id}
    API->>DB: Log visit
    DB->>API: ✅ Success
    API->>FE: Visit logged
    
    Note over DB: Data tích lũy<br/>ratings, favorites, visits
```

---

## Sơ Đồ 3: Luồng Training CF Model

```mermaid
flowchart TD
    START([Bắt đầu Training])
    CHECK{Kiểm tra<br/>Data}
    
    subgraph Conditions["📊 Điều kiện"]
        C1[≥5 users với ratings]
        C2[≥30 total ratings]
        C3[≥3 common destinations]
    end
    
    WAIT[❌ Chưa đủ data<br/>Thu thập thêm]
    
    subgraph Process["🔄 Training Process"]
        P1[1️⃣ Query data từ DB]
        P2[2️⃣ Build User-Item Matrix]
        P3[3️⃣ Compute User Similarity]
        P4[4️⃣ Compute Item Similarity]
        P5[5️⃣ Save to cf_model.pkl]
    end
    
    SUCCESS([✅ Model Ready])
    
    START --> CHECK
    CHECK -->|Đủ data| C1
    C1 --> C2
    C2 --> C3
    C3 --> P1
    
    CHECK -->|Chưa đủ| WAIT
    WAIT --> START
    
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> SUCCESS
    
    style START fill:#90EE90
    style SUCCESS fill:#90EE90
    style WAIT fill:#FFB6C1
    style Process fill:#E6E6FA
```

---

## Sơ Đồ 4: Luồng Hybrid Recommendation

```mermaid
flowchart TD
    REQUEST([User Request Tour])
    
    subgraph Input["📥 Input"]
        I1[user_id]
        I2[preferences]
        I3[budget]
        I4[time_available]
    end
    
    CHECK1{User có<br/>user_id?}
    CHECK2{User có<br/>≥3 ratings?}
    CHECK3{CF Model<br/>exists?}
    
    subgraph ContentBased["📋 Content-Based"]
        CB1[Filter by Type]
        CB2[Match Preferences]
        CB3[Score: 100%]
    end
    
    subgraph Collaborative["🤝 Collaborative Filtering"]
        CF1[Load cf_model.pkl]
        CF2[Find Similar Users]
        CF3[Predict Ratings]
        CF4[Score: 30%]
    end
    
    subgraph Hybrid["⚡ Hybrid Scoring"]
        H1[Combine Scores]
        H2[CF 30% + CB 70%]
        H3[Sort by Final Score]
    end
    
    subgraph Output["📤 Output"]
        O1[Top Destinations]
        O2[Optimize Route]
        O3[Build Tour]
    end
    
    RESPONSE([Personalized Tour])
    
    REQUEST --> Input
    Input --> CHECK1
    
    CHECK1 -->|No| ContentBased
    CHECK1 -->|Yes| CHECK2
    CHECK2 -->|No| ContentBased
    CHECK2 -->|Yes| CHECK3
    CHECK3 -->|No| ContentBased
    CHECK3 -->|Yes| Collaborative
    
    ContentBased --> CB1
    CB1 --> CB2
    CB2 --> CB3
    CB3 --> O1
    
    Collaborative --> CF1
    CF1 --> CF2
    CF2 --> CF3
    CF3 --> CF4
    CF4 --> Hybrid
    ContentBased --> Hybrid
    
    Hybrid --> H1
    H1 --> H2
    H2 --> H3
    H3 --> O1
    
    O1 --> O2
    O2 --> O3
    O3 --> RESPONSE
    
    style REQUEST fill:#90EE90
    style RESPONSE fill:#90EE90
    style ContentBased fill:#FFE4B5
    style Collaborative fill:#E0BBE4
    style Hybrid fill:#FFA07A
```

---

## Sơ Đồ 5: Cách CF Tìm Similar Users

```mermaid
graph TB
    subgraph Users["👥 USERS"]
        U1[User 1<br/>Thích biển]
        U2[User 2<br/>Thích văn hóa]
        U3[User 3<br/>Thích biển]
    end
    
    subgraph Ratings["⭐ RATINGS"]
        R1["Mỹ Khê: 5.0<br/>Sơn Trà: 4.5<br/>Chùa: 4.0"]
        R2["Bảo tàng: 5.0<br/>Hội An: 5.0<br/>Chùa: 4.0"]
        R3["Mỹ Khê: 5.0<br/>Sơn Trà: 4.0<br/>Cù Lao Chàm: 5.0"]
    end
    
    subgraph Matrix["🔢 USER-ITEM MATRIX"]
        M["
        Dest:  MK  ST  Chùa  BT  HA  CLC
        U1:   5.0 4.5  4.0   -   -   -
        U2:    -   -   4.0  5.0 5.0  -
        U3:   5.0 4.0   -    -   -  5.0
        "]
    end
    
    subgraph Similarity["📊 SIMILARITY"]
        S1["U1 ↔ U3<br/>Similarity: 92%"]
        S2["U1 ↔ U2<br/>Similarity: 35%"]
        S3["U2 ↔ U3<br/>Similarity: 20%"]
    end
    
    subgraph Prediction["🎯 PREDICTION"]
        P["U1 giống U3 (92%)<br/>U3 thích CLC (5.0)<br/>→ Predict: U1 sẽ thích CLC (4.8)"]
    end
    
    RECOMMEND["📍 RECOMMEND<br/>Cù Lao Chàm cho User 1"]
    
    U1 --> R1
    U2 --> R2
    U3 --> R3
    
    R1 --> Matrix
    R2 --> Matrix
    R3 --> Matrix
    
    Matrix --> Similarity
    
    S1 --> Prediction
    Prediction --> RECOMMEND
    
    style Users fill:#E1F5FF
    style Ratings fill:#FFF4E1
    style Matrix fill:#F0E1FF
    style Similarity fill:#FFE1F5
    style Prediction fill:#E1FFE1
    style RECOMMEND fill:#FFD700
```

---

## Sơ Đồ 6: Timeline Implementation

```mermaid
gantt
    title CF Implementation Timeline
    dateFormat YYYY-MM-DD
    section Phase 1: Setup
    Database Models           :done, p1, 2025-11-15, 1d
    Public APIs              :done, p2, 2025-11-16, 2d
    Testing APIs             :done, p3, 2025-11-18, 1d
    
    section Phase 2: CF Service
    CF Service Implementation :done, p4, 2025-11-18, 2d
    Training Scripts         :done, p5, 2025-11-19, 1d
    
    section Phase 3: Integration
    Hybrid Recommendation    :done, p6, 2025-11-20, 1d
    Fallback Mechanism       :done, p7, 2025-11-20, 1d
    Documentation           :done, p8, 2025-11-20, 1d
    
    section Phase 4: Deployment
    Data Collection         :active, p9, 2025-11-21, 7d
    Model Training          :p10, 2025-11-28, 1d
    Production Deploy       :p11, 2025-11-29, 1d
```

---

## Sơ Đồ 7: Architecture Overview

```mermaid
graph LR
    subgraph Client["🌐 CLIENT LAYER"]
        WEB[Web App]
        MOBILE[Mobile App]
    end
    
    subgraph API["📡 API LAYER"]
        AUTH[Auth APIs]
        CF_API[CF APIs<br/>ratings/favorites<br/>visits/feedback]
        TOUR[Tour APIs]
    end
    
    subgraph Service["⚙️ SERVICE LAYER"]
        AUTH_SVC[Auth Service]
        CF_SVC[CF Service]
        TOUR_SVC[Tour Service]
        DEST_SVC[Destination Service]
    end
    
    subgraph Data["💾 DATA LAYER"]
        DB[(PostgreSQL<br/>Neon)]
        MODEL[cf_model.pkl]
    end
    
    WEB --> API
    MOBILE --> API
    
    AUTH --> AUTH_SVC
    CF_API --> CF_SVC
    TOUR --> TOUR_SVC
    TOUR --> CF_SVC
    
    AUTH_SVC --> DB
    CF_SVC --> DB
    CF_SVC --> MODEL
    TOUR_SVC --> CF_SVC
    TOUR_SVC --> DEST_SVC
    DEST_SVC --> DB
    
    style Client fill:#E1F5FF
    style API fill:#FFF4E1
    style Service fill:#F0E1FF
    style Data fill:#E1FFE1
```

---

## 🎨 Hướng Dẫn Sử Dụng Trong Slide

### Cách 1: Render trực tiếp (GitHub, Notion, GitLab)
- Copy code Mermaid vào markdown
- Tự động render thành diagram

### Cách 2: Export sang hình ảnh

**Online Tools:**
1. **Mermaid Live Editor**: https://mermaid.live/
   - Paste code Mermaid
   - Click "Download PNG" hoặc "Download SVG"

2. **Diagrams.net (draw.io)**: https://app.diagrams.net/
   - Import Mermaid code
   - Export PNG/SVG

3. **VS Code Extension**:
   - Install "Markdown Preview Mermaid Support"
   - Right-click diagram → Export to PNG

### Cách 3: Screenshot
- Render diagram trong GitHub/Notion
- Screenshot và crop

---

## 📋 Checklist Cho Slide

- [ ] **Slide 1**: Sơ đồ 1 - Tổng quan hệ thống
- [ ] **Slide 2**: Sơ đồ 2 - Luồng thu thập dữ liệu
- [ ] **Slide 3**: Sơ đồ 5 - Cách CF tìm similar users (ví dụ)
- [ ] **Slide 4**: Sơ đồ 4 - Luồng Hybrid Recommendation
- [ ] **Slide 5**: Sơ đồ 7 - Architecture overview

---

## 💡 Tips Cho Presentation

1. **Bắt đầu với Sơ đồ 5** (Similar Users) - dễ hiểu nhất
2. **Sau đó Sơ đồ 1** (Tổng quan) - big picture
3. **Chi tiết với Sơ đồ 4** (Hybrid) - implementation
4. **Kết với Sơ đồ 7** (Architecture) - technical depth

**Animation suggestions:**
- Highlight từng bước trong flow
- Màu sắc đã được set sẵn cho từng layer
- Focus vào arrows để show data flow

---

**Chúc bạn thuyết trình thành công với những diagram đẹp! 🎨🚀**

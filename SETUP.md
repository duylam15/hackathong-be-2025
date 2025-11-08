# Hướng dẫn Setup dự án Hackathon Backend

## Bước 1: Cài đặt dependencies

```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
.\venv\Scripts\activate

# Cài đặt các packages
pip install -r requirements.txt
```

## Bước 2: Cấu hình Database (Neon PostgreSQL)

1. Đăng ký tài khoản tại https://neon.tech
2. Tạo một project mới
3. Copy connection string
4. Tạo file `.env` từ `.env.example`:

```powershell
copy .env.example .env
```

5. Cập nhật thông tin trong file `.env`:

```env
DATABASE_URL=postgresql://username:password@ep-xxxxx-xxxxx.region.aws.neon.tech/dbname?sslmode=require
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=hackathon_db
POSTGRES_HOST=ep-xxxxx-xxxxx.region.aws.neon.tech
POSTGRES_PORT=5432

SECRET_KEY=your-super-secret-key-change-this-in-production
```

## Bước 3: Khởi tạo Database

```powershell
# Chạy script khởi tạo database và seed data mẫu
python init_db.py
```

## Bước 4: Chạy ứng dụng

### Development mode (với auto-reload):
```powershell
uvicorn app.main:app --reload
```

### Hoặc chạy trực tiếp:
```powershell
python -m app.main
```

## Bước 5: Kiểm tra

Mở trình duyệt và truy cập:

- **API Root**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Bước 6: Test API

### Sử dụng Swagger UI (khuyến nghị):
1. Truy cập http://localhost:8000/docs
2. Thử các endpoints:
   - GET `/api/v1/users` - Lấy danh sách users
   - POST `/api/v1/users` - Tạo user mới
   - GET `/api/v1/destinations` - Lấy danh sách destinations

### Hoặc sử dụng curl:

```powershell
# Get all users
curl http://localhost:8000/api/v1/users

# Get all destinations
curl http://localhost:8000/api/v1/destinations

# Create a new user
curl -X POST http://localhost:8000/api/v1/users `
  -H "Content-Type: application/json" `
  -d '{\"full_name\":\"Test User\",\"email\":\"test@example.com\"}'
```

## Bước 7: Setup Database Migrations (Optional)

```powershell
# Khởi tạo Alembic
alembic init alembic

# Tạo migration đầu tiên
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## Cấu trúc thư mục sau khi setup:

```
Hackathon/
├── app/                    # Source code chính
│   ├── api/               # API endpoints
│   ├── core/              # Configuration
│   ├── db/                # Database setup
│   ├── models/            # ORM models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── tests/                 # Unit tests
├── venv/                  # Virtual environment
├── .env                   # Environment variables (không commit)
├── .env.example           # Template for .env
├── .gitignore            
├── requirements.txt       # Python dependencies
├── init_db.py            # Database initialization script
└── README.md             # Documentation
```

## Troubleshooting

### Lỗi kết nối database:
- Kiểm tra connection string trong `.env`
- Đảm bảo Neon database đang chạy
- Kiểm tra firewall/network settings

### Lỗi import modules:
```powershell
# Đảm bảo đang ở trong virtual environment
.\venv\Scripts\activate

# Cài đặt lại dependencies
pip install -r requirements.txt
```

### Lỗi port đã được sử dụng:
```powershell
# Chạy trên port khác
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. Implement authentication endpoints
2. Add more business logic trong services
3. Write comprehensive tests
4. Setup CI/CD pipeline
5. Add API rate limiting
6. Implement caching với Redis
7. Add logging và monitoring

## Tài liệu tham khảo

- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://www.sqlalchemy.org
- Neon: https://neon.tech/docs
- Pydantic: https://docs.pydantic.dev

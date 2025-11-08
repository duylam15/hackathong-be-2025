"""
Script to initialize the database with sample data
"""
from app.db.database import engine, SessionLocal
from app.models import Base, User, Company, Destination, DestinationCategory
from datetime import datetime, date


def init_db():
    """Initialize database with tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def seed_data():
    """Seed the database with sample data"""
    db = SessionLocal()
    
    try:
        print("\nSeeding sample data...")
        
        # Create sample users
        users = [
            User(
                full_name="John Doe",
                email="john@example.com",
                phone="0901234567",
                date_of_birth=date(1990, 1, 1),
                status="active"
            ),
            User(
                full_name="Jane Smith",
                email="jane@example.com",
                phone="0907654321",
                date_of_birth=date(1992, 5, 15),
                status="active"
            )
        ]
        db.add_all(users)
        db.commit()
        print("✓ Created sample users")
        
        # Create sample company
        company = Company(
            company_name="Vietnam Tourism",
            address="123 Nguyen Hue, Ho Chi Minh City",
            phone="0281234567",
            email="info@vietnam-tourism.com",
            status="active"
        )
        db.add(company)
        db.commit()
        print("✓ Created sample company")
        
        # Create sample categories
        categories = [
            DestinationCategory(
                category_name="Historical",
                category_description="Historical sites and landmarks",
                icon="🏛️"
            ),
            DestinationCategory(
                category_name="Natural",
                category_description="Natural attractions and parks",
                icon="🏞️"
            ),
            DestinationCategory(
                category_name="Cultural",
                category_description="Cultural sites and museums",
                icon="🎭"
            )
        ]
        db.add_all(categories)
        db.commit()
        print("✓ Created sample categories")
        
        # Create sample destinations
        destinations = [
            Destination(
                company_id=company.company_id,
                destination_name="Notre Dame Cathedral",
                location_address="01 Cong xa Paris, Ben Nghe Ward, District 1, HCMC",
                latitude=10.7797,
                longitude=106.6990,
                destination_type="Historical",
                popularity_score=95,
                avg_duration=45,
                is_active=True
            ),
            Destination(
                company_id=company.company_id,
                destination_name="Ben Thanh Market",
                location_address="Le Loi, Ben Thanh Ward, District 1, HCMC",
                latitude=10.7725,
                longitude=106.6980,
                destination_type="Cultural",
                popularity_score=90,
                avg_duration=120,
                is_active=True
            )
        ]
        db.add_all(destinations)
        db.commit()
        print("✓ Created sample destinations")
        
        print("\n✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("Database Initialization Script")
    print("=" * 50)
    
    init_db()
    
    response = input("\nDo you want to seed sample data? (y/n): ")
    if response.lower() == 'y':
        seed_data()
    
    print("\n" + "=" * 50)
    print("Done!")
    print("=" * 50)

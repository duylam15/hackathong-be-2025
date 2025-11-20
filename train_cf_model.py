"""
Train Collaborative Filtering Model
====================================
Script này dùng để train CF model từ dữ liệu ratings/favorites/visits

Usage:
    python train_cf_model.py

Requirements:
    - Tối thiểu 5 users với 3+ ratings mỗi người
    - Có ít nhất 2 destinations được rate bởi nhiều users
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.destination_rating import DestinationRating
from app.models.user_favorite import UserFavorite
from app.models.visit_log import VisitLog
from app.models.destination import Destination
from app.services.collaborative_filtering_service import CollaborativeFilteringService
import pickle
import numpy as np
from datetime import datetime


def check_data_readiness(db: Session) -> dict:
    """Check if we have enough data to train CF model"""
    
    print("\n" + "="*60)
    print("📊 CHECKING DATA READINESS FOR CF TRAINING")
    print("="*60)
    
    # Count users with ratings
    users_with_ratings = db.query(
        func.count(func.distinct(DestinationRating.user_id))
    ).scalar()
    
    # Count total ratings
    total_ratings = db.query(func.count(DestinationRating.id)).scalar()
    
    # Count destinations with multiple ratings
    destinations_with_multi_ratings = db.query(DestinationRating.destination_id)\
        .group_by(DestinationRating.destination_id)\
        .having(func.count(DestinationRating.id) >= 2)\
        .count()
    
    # Count favorites
    total_favorites = db.query(func.count(UserFavorite.id)).scalar()
    
    # Count visits
    total_visits = db.query(func.count(VisitLog.id)).scalar()
    
    # Count total destinations
    total_destinations = db.query(func.count(Destination.id)).scalar()
    
    # Check if ready
    is_ready = (
        users_with_ratings >= 5 and
        total_ratings >= 30 and
        destinations_with_multi_ratings >= 3
    )
    
    status = {
        "ready": is_ready,
        "users_with_ratings": users_with_ratings,
        "total_ratings": total_ratings,
        "total_favorites": total_favorites,
        "total_visits": total_visits,
        "total_destinations": total_destinations,
        "destinations_with_multi_ratings": destinations_with_multi_ratings,
    }
    
    # Print status
    print(f"\n📈 Current Data Status:")
    print(f"   • Users with ratings:     {users_with_ratings:>3} {'✅' if users_with_ratings >= 5 else '❌'} (need ≥5)")
    print(f"   • Total ratings:          {total_ratings:>3} {'✅' if total_ratings >= 30 else '❌'} (need ≥30)")
    print(f"   • Common destinations:    {destinations_with_multi_ratings:>3} {'✅' if destinations_with_multi_ratings >= 3 else '❌'} (need ≥3)")
    print(f"   • Total favorites:        {total_favorites:>3}")
    print(f"   • Total visits:           {total_visits:>3}")
    print(f"   • Total destinations:     {total_destinations:>3}")
    
    if is_ready:
        print(f"\n✅ DATA IS READY! You can train the CF model now.")
    else:
        print(f"\n❌ NOT ENOUGH DATA YET")
        print(f"\n💡 What you need:")
        if users_with_ratings < 5:
            print(f"   - Need {5 - users_with_ratings} more users with ratings")
        if total_ratings < 30:
            print(f"   - Need {30 - total_ratings} more ratings")
        if destinations_with_multi_ratings < 3:
            print(f"   - Need more users to rate the same destinations")
        
        print(f"\n📝 Tips:")
        print(f"   - Ask 5-10 people to test the app")
        print(f"   - Each person should rate 3-5 destinations")
        print(f"   - Make sure they rate some common places")
    
    print("="*60 + "\n")
    
    return status


def train_cf_model(db: Session) -> bool:
    """Train and save CF model"""
    
    print("\n" + "="*60)
    print("🧠 TRAINING COLLABORATIVE FILTERING MODEL")
    print("="*60)
    
    try:
        # Initialize CF service
        cf_service = CollaborativeFilteringService(db)
        
        print("\n1️⃣ Building user-item interaction matrix...")
        matrix, user_ids, dest_ids = cf_service.build_interaction_matrix()
        print(f"   ✅ Matrix shape: {matrix.shape} (users × destinations)")
        print(f"   ✅ User IDs: {user_ids}")
        print(f"   ✅ Destination IDs: {dest_ids}")
        
        print("\n2️⃣ Computing user-user similarities...")
        cf_service.compute_user_similarity()
        print(f"   ✅ User similarity matrix: {cf_service.user_similarity.shape}")
        
        print("\n3️⃣ Computing item-item similarities...")
        cf_service.compute_item_similarity()
        print(f"   ✅ Item similarity matrix: {cf_service.item_similarity.shape}")
        
        print("\n4️⃣ Saving model to disk...")
        model_data = {
            "user_item_matrix": matrix,
            "user_similarity": cf_service.user_similarity,
            "item_similarity": cf_service.item_similarity,
            "user_ids": user_ids,
            "dest_ids": dest_ids,
            "trained_at": datetime.now().isoformat(),
            "n_users": len(user_ids),
            "n_destinations": len(dest_ids),
            "n_ratings": np.count_nonzero(matrix)
        }
        
        model_path = Path(__file__).parent / "cf_model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model_data, f)
        
        print(f"   ✅ Model saved to: {model_path}")
        print(f"\n📊 Model Statistics:")
        print(f"   • Number of users:        {model_data['n_users']}")
        print(f"   • Number of destinations: {model_data['n_destinations']}")
        print(f"   • Number of ratings:      {model_data['n_ratings']}")
        print(f"   • Matrix density:         {model_data['n_ratings'] / (model_data['n_users'] * model_data['n_destinations']) * 100:.2f}%")
        print(f"   • Trained at:             {model_data['trained_at']}")
        
        print("\n✅ CF MODEL TRAINING COMPLETED!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during training: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60 + "\n")
        return False


def view_sample_data(db: Session):
    """View sample ratings data"""
    
    print("\n" + "="*60)
    print("👀 SAMPLE DATA")
    print("="*60)
    
    # Get sample ratings
    ratings = db.query(DestinationRating).limit(10).all()
    
    if ratings:
        print("\n📋 Sample Ratings:")
        for r in ratings:
            print(f"   User {r.user_id} → Destination {r.destination_id}: {r.rating}⭐")
    else:
        print("\n❌ No ratings found in database")
    
    # Get sample favorites
    favorites = db.query(UserFavorite).limit(5).all()
    if favorites:
        print(f"\n❤️ Sample Favorites:")
        for f in favorites:
            print(f"   User {f.user_id} → Destination {f.destination_id}")
    
    # Get sample visits
    visits = db.query(VisitLog).limit(5).all()
    if visits:
        print(f"\n✈️ Sample Visits:")
        for v in visits:
            print(f"   User {v.user_id} → Destination {v.destination_id}")
    
    print("="*60 + "\n")


def main():
    """Main function"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "CF MODEL TRAINING SCRIPT" + " "*19 + "║")
    print("╚" + "="*58 + "╝")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check data readiness
        status = check_data_readiness(db)
        
        # View sample data
        view_sample_data(db)
        
        # Train if ready
        if status["ready"]:
            response = input("\n🤔 Do you want to train the CF model now? (y/n): ")
            if response.lower() in ['y', 'yes']:
                success = train_cf_model(db)
                if success:
                    print("\n🎉 SUCCESS! CF model is ready to use.")
                    print("   You can now use CF recommendations in your tours.")
                else:
                    print("\n❌ Training failed. Check the errors above.")
            else:
                print("\n⏭️ Training skipped.")
        else:
            print("\n💡 Keep collecting data! Run this script again when you have more ratings.")
    
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()

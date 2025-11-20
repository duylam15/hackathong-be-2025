"""
Quick Check CF Model Status
============================
Script nhanh để check xem CF model đã sẵn sàng chưa

Usage:
    python check_cf_status.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import func
from app.db.database import SessionLocal
from app.models.destination_rating import DestinationRating
from app.models.user_favorite import UserFavorite
from app.models.visit_log import VisitLog
from app.models.destination import Destination
from app.models.user import User


def main():
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("📊 CF MODEL STATUS CHECK")
        print("="*60)
        
        # Check ratings
        users_with_ratings = db.query(
            func.count(func.distinct(DestinationRating.user_id))
        ).scalar()
        
        total_ratings = db.query(func.count(DestinationRating.id)).scalar()
        
        destinations_multi = db.query(DestinationRating.destination_id)\
            .group_by(DestinationRating.destination_id)\
            .having(func.count(DestinationRating.id) >= 2)\
            .count()
        
        total_favorites = db.query(func.count(UserFavorite.id)).scalar()
        total_visits = db.query(func.count(VisitLog.id)).scalar()
        total_destinations = db.query(func.count(Destination.id)).scalar()
        total_users = db.query(func.count(User.id)).scalar()
        
        # Check model file
        model_path = Path(__file__).parent / "cf_model.pkl"
        model_exists = model_path.exists()
        
        print(f"\n📈 Data Collected:")
        print(f"   Total users:              {total_users}")
        print(f"   Users with ratings:       {users_with_ratings} {'✅' if users_with_ratings >= 5 else '❌ (need ≥5)'}")
        print(f"   Total ratings:            {total_ratings} {'✅' if total_ratings >= 30 else '❌ (need ≥30)'}")
        print(f"   Total favorites:          {total_favorites}")
        print(f"   Total visits:             {total_visits}")
        print(f"   Total destinations:       {total_destinations}")
        print(f"   Common destinations:      {destinations_multi} {'✅' if destinations_multi >= 3 else '❌ (need ≥3)'}")
        
        print(f"\n🧠 CF Model:")
        if model_exists:
            import pickle
            with open(model_path, "rb") as f:
                model_data = pickle.load(f)
            print(f"   Status:                   ✅ TRAINED")
            print(f"   Trained at:               {model_data['trained_at']}")
            print(f"   Users in model:           {model_data['n_users']}")
            print(f"   Destinations in model:    {model_data['n_destinations']}")
            print(f"   Total ratings:            {model_data['n_ratings']}")
        else:
            print(f"   Status:                   ❌ NOT TRAINED")
            print(f"   Model file:               Not found")
        
        # Overall status
        is_ready = users_with_ratings >= 5 and total_ratings >= 30 and destinations_multi >= 3
        
        print(f"\n🎯 Overall Status:")
        if model_exists:
            print(f"   ✅ CF MODEL IS READY TO USE!")
        elif is_ready:
            print(f"   ⚠️ DATA IS READY - Need to train model")
            print(f"   Run: python train_cf_model.py")
        else:
            print(f"   ❌ NOT ENOUGH DATA YET")
            print(f"\n   What you need:")
            if users_with_ratings < 5:
                print(f"     • {5 - users_with_ratings} more users with ratings")
            if total_ratings < 30:
                print(f"     • {30 - total_ratings} more ratings")
            if destinations_multi < 3:
                print(f"     • More overlap (users rating same destinations)")
        
        print("="*60 + "\n")
        
        # Show detailed ratings breakdown
        if total_ratings > 0:
            print("📊 Ratings Breakdown by User:")
            ratings_per_user = db.query(
                DestinationRating.user_id,
                func.count(DestinationRating.id).label('count')
            ).group_by(DestinationRating.user_id).all()
            
            for user_id, count in ratings_per_user:
                status_icon = "✅" if count >= 3 else "⚠️"
                print(f"   {status_icon} User {user_id}: {count} ratings")
            
            print("\n📊 Most Rated Destinations:")
            top_destinations = db.query(
                Destination.name,
                func.count(DestinationRating.id).label('count'),
                func.avg(DestinationRating.rating).label('avg_rating')
            ).join(DestinationRating).group_by(Destination.id, Destination.name)\
             .order_by(func.count(DestinationRating.id).desc())\
             .limit(10).all()
            
            for dest_name, count, avg_rating in top_destinations:
                print(f"   • {dest_name}: {count} ratings (avg: {avg_rating:.1f}⭐)")
            
            print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

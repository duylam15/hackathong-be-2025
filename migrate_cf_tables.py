"""
Migration script to create Collaborative Filtering tables
Run this script to add the new CF-related tables to the database.

Tables to be created:
- destination_ratings
- user_favorites  
- visit_logs
- user_feedback

And update destination table with new columns.
"""

from app.db.database import engine, Base
from app.models import (
    DestinationRating,
    UserFavorite,
    VisitLog,
    UserFeedback,
    Destination
)
from sqlalchemy import inspect, text
import sys


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_cf_tables():
    """Run the migration to create CF tables and update destination table."""
    
    print("🚀 Starting Collaborative Filtering Migration...")
    print("=" * 60)
    
    try:
        # Check existing tables
        print("\n📋 Checking existing tables...")
        new_tables = ['destination_ratings', 'user_favorites', 'visit_logs', 'user_feedback']
        existing_tables = []
        
        for table in new_tables:
            if check_table_exists(table):
                existing_tables.append(table)
                print(f"  ⚠️  Table '{table}' already exists")
            else:
                print(f"  ✅ Table '{table}' will be created")
        
        # Create all tables (will skip existing ones)
        print("\n🔨 Creating new tables...")
        Base.metadata.create_all(bind=engine)
        print("  ✅ Tables created successfully")
        
        # Check and add new columns to destination table
        print("\n🔧 Updating destination table with new CF columns...")
        
        # Get actual table name from inspector
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        dest_table = None
        for tbl in table_names:
            if 'destination' in tbl.lower() and 'rating' not in tbl.lower():
                dest_table = tbl
                break
        
        if not dest_table:
            print("  ⚠️  Could not find destination table")
        else:
            with engine.connect() as conn:
                new_columns = {
                    'avg_rating': 'FLOAT DEFAULT 0.0',
                    'total_ratings': 'INTEGER DEFAULT 0',
                    'total_visits': 'INTEGER DEFAULT 0',
                    'total_favorites': 'INTEGER DEFAULT 0',
                    'popularity_score': 'FLOAT DEFAULT 0.0',
                    'last_stats_update': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
                }
                
                for col_name, col_type in new_columns.items():
                    if not check_column_exists(dest_table, col_name):
                        try:
                            sql = text(f"ALTER TABLE {dest_table} ADD COLUMN {col_name} {col_type}")
                            conn.execute(sql)
                            conn.commit()
                            print(f"  ✅ Added column '{col_name}' to {dest_table} table")
                        except Exception as e:
                            print(f"  ⚠️  Could not add column '{col_name}': {e}")
                    else:
                        print(f"  ℹ️  Column '{col_name}' already exists in {dest_table} table")
        
        # Create indexes for better performance
        print("\n📊 Creating indexes for better query performance...")
        
        with engine.connect() as conn:
            indexes = [
                # DestinationRating indexes
                ("idx_rating_user", "destination_ratings", "user_id"),
                ("idx_rating_dest", "destination_ratings", "destination_id"),
                ("idx_rating_created", "destination_ratings", "created_at"),
                
                # UserFavorite indexes
                ("idx_favorite_user", "user_favorites", "user_id"),
                ("idx_favorite_dest", "user_favorites", "destination_id"),
                
                # VisitLog indexes
                ("idx_visit_user", "visit_logs", "user_id"),
                ("idx_visit_dest", "visit_logs", "destination_id"),
                ("idx_visit_date", "visit_logs", "visited_at"),
                
                # UserFeedback indexes
                ("idx_feedback_user", "user_feedback", "user_id"),
                ("idx_feedback_dest", "user_feedback", "destination_id"),
                ("idx_feedback_type", "user_feedback", "feedback_type"),
            ]
            
            for idx_name, table_name, column_name in indexes:
                try:
                    # Check if index exists
                    inspector = inspect(engine)
                    existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
                    
                    if idx_name not in existing_indexes:
                        sql = text(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})")
                        conn.execute(sql)
                        conn.commit()
                        print(f"  ✅ Created index '{idx_name}' on {table_name}({column_name})")
                    else:
                        print(f"  ℹ️  Index '{idx_name}' already exists")
                except Exception as e:
                    print(f"  ⚠️  Could not create index '{idx_name}': {e}")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("\n📝 Summary:")
        print(f"  • Created {len(new_tables)} new tables for CF")
        print(f"  • Updated destination table with {len(new_columns)} new columns")
        print(f"  • Created {len(indexes)} indexes for performance")
        print("\n🎉 Your database is now ready for Collaborative Filtering!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  1. Check your database connection settings")
        print("  2. Ensure you have proper database permissions")
        print("  3. Check the error message above for details")
        sys.exit(1)


def rollback_cf_tables():
    """Rollback the CF migration (drop tables and columns)."""
    print("\n⚠️  WARNING: This will delete all CF data!")
    response = input("Are you sure you want to rollback? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Rollback cancelled.")
        return
    
    print("\n🔄 Rolling back CF migration...")
    
    try:
        with engine.connect() as conn:
            # Drop tables
            tables = ['user_feedback', 'visit_logs', 'user_favorites', 'destination_ratings']
            for table in tables:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    conn.commit()
                    print(f"  ✅ Dropped table '{table}'")
                except Exception as e:
                    print(f"  ⚠️  Could not drop table '{table}': {e}")
            
            # Drop columns from destination table
            columns = ['avg_rating', 'total_ratings', 'total_visits', 'total_favorites', 
                      'popularity_score', 'last_stats_update']
            for col in columns:
                try:
                    conn.execute(text(f"ALTER TABLE destinations DROP COLUMN IF EXISTS {col}"))
                    conn.commit()
                    print(f"  ✅ Dropped column '{col}' from destinations")
                except Exception as e:
                    print(f"  ⚠️  Could not drop column '{col}': {e}")
        
        print("\n✅ Rollback completed!")
        
    except Exception as e:
        print(f"\n❌ Rollback failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage CF database migrations')
    parser.add_argument(
        'action',
        choices=['migrate', 'rollback', 'status'],
        help='Action to perform: migrate, rollback, or status'
    )
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        migrate_cf_tables()
    elif args.action == 'rollback':
        rollback_cf_tables()
    elif args.action == 'status':
        print("\n📊 Database Migration Status")
        print("=" * 60)
        
        tables = ['destination_ratings', 'user_favorites', 'visit_logs', 'user_feedback']
        for table in tables:
            status = "✅ EXISTS" if check_table_exists(table) else "❌ MISSING"
            print(f"  {table}: {status}")
        
        # Find destination table
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        dest_table = None
        for tbl in table_names:
            if 'destination' in tbl.lower() and 'rating' not in tbl.lower():
                dest_table = tbl
                break
        
        if dest_table:
            print(f"\n  {dest_table} table:")
            columns = ['avg_rating', 'total_ratings', 'total_visits', 'total_favorites', 
                      'popularity_score', 'last_stats_update']
            for col in columns:
                status = "✅ EXISTS" if check_column_exists(dest_table, col) else "❌ MISSING"
                print(f"    {col}: {status}")
        
        print("=" * 60)

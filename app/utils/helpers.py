from datetime import datetime
from typing import Optional


def format_datetime(dt: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """Format datetime object to string"""
    if dt is None:
        return None
    return dt.strftime(format_str)


def calculate_duration(start_time, end_time) -> int:
    """Calculate duration in minutes between two time objects"""
    if not start_time or not end_time:
        return 0
    
    # Convert to datetime for calculation
    start = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)
    
    # Handle case where end time is next day
    if end < start:
        end = datetime.combine(datetime.today().replace(day=datetime.today().day + 1), end_time)
    
    duration = (end - start).total_seconds() / 60
    return int(duration)


def paginate_response(items: list, total: int, skip: int, limit: int) -> dict:
    """Create paginated response"""
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime, time


class ItineraryDestinationBase(BaseModel):
    """Base Itinerary Destination schema"""
    destination_id: int
    day_number: int
    visit_order: int
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class ItineraryDestinationCreate(ItineraryDestinationBase):
    """Schema for creating an itinerary destination"""
    pass


class ItineraryDestinationInDB(ItineraryDestinationBase):
    """Schema for itinerary destination in database"""
    itinerary_dest_id: int
    itinerary_id: int
    
    class Config:
        from_attributes = True


class ItineraryDestinationResponse(ItineraryDestinationInDB):
    """Schema for itinerary destination response"""
    pass


# Itinerary schemas
class ItineraryBase(BaseModel):
    """Base Itinerary schema"""
    itinerary_name: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_days: Optional[int] = None


class ItineraryCreate(ItineraryBase):
    """Schema for creating an itinerary"""
    user_id: int
    user_type_id: Optional[int] = None
    trend_id: Optional[int] = None


class ItineraryUpdate(BaseModel):
    """Schema for updating an itinerary"""
    itinerary_name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    total_days: Optional[int] = None
    status: Optional[str] = None


class ItineraryInDB(ItineraryBase):
    """Schema for itinerary in database"""
    itinerary_id: int
    user_id: int
    user_type_id: Optional[int]
    trend_id: Optional[int]
    total_destinations: int
    status: str
    created_date: datetime
    updated_date: datetime
    
    class Config:
        from_attributes = True


class ItineraryResponse(ItineraryInDB):
    """Schema for itinerary response"""
    destinations: List[ItineraryDestinationResponse] = []


class ItineraryWithDetails(ItineraryResponse):
    """Schema for itinerary with full details"""
    pass

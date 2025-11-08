from fastapi import APIRouter
from app.api.v1.endpoints import users, destinations, itineraries

# Create API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    destinations.router,
    prefix="/destinations",
    tags=["destinations"]
)

api_router.include_router(
    itineraries.router,
    prefix="/itineraries",
    tags=["itineraries"]
)

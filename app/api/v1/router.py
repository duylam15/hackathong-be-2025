from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, destinations, quiz, tours, tags

# Create API v1 router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

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
    quiz.router,
    prefix="/quiz",
    tags=["quiz"]
)

api_router.include_router(
    tours.router,
    prefix="/tours",
    tags=["tours"]
)

api_router.include_router(
    tags.router,
    prefix="/tags",
    tags=["tags"]
)

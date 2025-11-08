from .users import router as users_router
from .destinations import router as destinations_router
from .itineraries import router as itineraries_router
from .quiz import router as quiz_router
from .auth import router as auth_router

__all__ = [
    "users_router",
    "destinations_router",
    "itineraries_router",
    "quiz_router",
    "auth_router"
]

from fastapi import APIRouter

from fastapi import APIRouter
from .studentgpt import router as studentgpt_router
from .classroom import router as classroom_router
from app.api.v1.endpoints import health, refiner

api_router = APIRouter()

# Register StudentGPT and Classroom routers with prefixes
api_router.include_router(studentgpt_router, prefix="/studentgpt", tags=["studentgpt"])
api_router.include_router(classroom_router, prefix="/classroom", tags=["classroom"])

# Include health and refiner endpoints
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(refiner.router, prefix="", tags=["refiner"])
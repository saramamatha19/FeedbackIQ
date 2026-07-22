from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, dashboard, exports, feedback, uploads

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(uploads.router)
api_router.include_router(feedback.router)
api_router.include_router(dashboard.router)
api_router.include_router(exports.router)
api_router.include_router(admin.router)

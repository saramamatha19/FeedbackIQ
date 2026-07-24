from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(title="FeedbackIQ API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    #allow cookies
    allow_credentials=True,
    allow_methods=["*"],
    #allow all request headers
    allow_headers=["*"],
)
#this connects all endpoints to the application.
app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}

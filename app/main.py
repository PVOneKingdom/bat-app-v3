from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from app.exception.web import (
    NonHTMXRequestException,
    RedirectToLoginException,
    non_htmx_request_exception_handler,
    redirect_to_login_exception_handler,
)
from pathlib import Path

from app.config import FORCE_HTTPS_PATHS_ENV, APP_ROOT, DATA_ROOT, DB_DIR, UPLOADS_DIR

from app.service.user import add_default_user
from app.service.question import add_default_questions

from app.api.auth import router as auth_api_router

from app.web.public import router as public_router
from app.web.dashboard.dashboard import router as dashboard_router
from app.web.dashboard.users import router as dashboard_users_router
from app.web.dashboard.questions import router as dashboard_questions_router
from app.web.dashboard.assessments import router as dashboard_assessments_router
from app.web.dashboard.reports import router as dashboard_reports_router

from app.web.app import router as app_root_router
from app.web.app.assessments import router as app_assessments_router
from app.web.app.reports import router as app_reports_router
from app.web.app.profile import router as app_profile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure required directories exist before app starts
    # Single volume structure: /app/data/ contains all persistent data
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    add_default_user()
    add_default_questions()

    yield


# Main app to start
app = FastAPI(lifespan=lifespan)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Force request.scheme to 'https'
        request.scope["scheme"] = "https"
        return await call_next(request)


if FORCE_HTTPS_PATHS_ENV:
    app.add_middleware(HTTPSRedirectMiddleware)


app.add_exception_handler(NonHTMXRequestException, non_htmx_request_exception_handler)
app.add_exception_handler(RedirectToLoginException, redirect_to_login_exception_handler)

# Mount static files directories
app.mount("/js", StaticFiles(directory=APP_ROOT / "static" / "js"), name="js")
app.mount("/css", StaticFiles(directory=APP_ROOT / "static" / "css"), name="css")
app.mount("/images", StaticFiles(directory=APP_ROOT / "static" / "images"), name="images")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Routers

# API routers
app.include_router(auth_api_router, prefix="/api/v1/auth")

# Dashboard routers
app.include_router(public_router)
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(dashboard_users_router, prefix="/dashboard/users")
app.include_router(dashboard_questions_router, prefix="/dashboard/questions")
app.include_router(dashboard_assessments_router, prefix="/dashboard/assessments")
app.include_router(dashboard_reports_router, prefix="/dashboard/reports")

# App routers
app.include_router(app_root_router, prefix="/app")
app.include_router(app_assessments_router, prefix="/app/assessments")
app.include_router(app_reports_router, prefix="/app/reports")
app.include_router(app_profile_router, prefix="/app/profile")

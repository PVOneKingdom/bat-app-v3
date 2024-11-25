from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.exception.web import NonHTMXRequestException, RedirectToLoginException, non_htmx_request_exception_handler, redirect_to_login_exception_handler
from pathlib import Path


from app.web.public import router as public_router
from app.web.dashboard.dashboard import router as dashboard_router
from app.web.dashboard.users import router as dashboard_users_router
from app.web.dashboard.questions import router as dashboard_questions_router


# Main app to start
app = FastAPI()

app.add_exception_handler(NonHTMXRequestException, non_htmx_request_exception_handler)
app.add_exception_handler(RedirectToLoginException, redirect_to_login_exception_handler)

# Mount static files directories
static_dir = Path(__file__).resolve().parent
app.mount("/js", StaticFiles(directory=static_dir / "static" / "js"), name="js")
app.mount("/css", StaticFiles(directory=static_dir / "static" / "css"), name="css")
app.mount("/images", StaticFiles(directory=static_dir / "static" / "images"), name="images")

# Routers
app.include_router(public_router)
app.include_router(dashboard_router, prefix="/dashboard")
app.include_router(dashboard_users_router, prefix="/dashboard/users")
app.include_router(dashboard_questions_router, prefix="/dashboard/questions")

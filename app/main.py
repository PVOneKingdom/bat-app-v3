from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.exception.web import NonHTMXRequestException, non_htmx_request_exception_handler
from app.web.public import router as public_router
from pathlib import Path


# Main app to start
app = FastAPI()

app.add_exception_handler(NonHTMXRequestException, non_htmx_request_exception_handler)

# Mount static files directories

static_dir = Path(__file__).resolve().parent
app.mount("/js", StaticFiles(directory=static_dir / "static" / "js"), name="js")
app.mount("/css", StaticFiles(directory=static_dir / "static" / "css"), name="css")
app.mount("/images", StaticFiles(directory=static_dir / "static" / "images"), name="images")

# Routers
app.include_router(public_router)

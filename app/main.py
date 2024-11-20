from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.exception.web import NonHTMXRequestException, non_htmx_request_exception_handler
from app.web.public import router as public_router


# Main app to start
app = FastAPI()

app.add_exception_handler(NonHTMXRequestException, non_htmx_request_exception_handler)

# Mount static files directories
app.mount("/js", StaticFiles(directory="static/js"), name="js")
app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/images", StaticFiles(directory="static/images"), name="images")

# Routers
app.include_router(public_router)

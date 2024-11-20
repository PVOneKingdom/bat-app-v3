from fastapi import HTTPException, Request, Response
from app.template.init import jinja

class NonHTMXRequestException(HTTPException):
    def __init__(self, detail: str = "Unauthorized - Non HTMX Request"):
        super().__init__(status_code=401, detail=detail)

async def non_htmx_request_exception_handler(request: Request, exc: Exception) -> Response:
    context = {
            "request": request,
            "title":"Loading...",
            "description":"Loading the page. Please wait.",
            "path": request.url,
            }

    return jinja.TemplateResponse(
            name="non-htmx-to-htmx.html",
            context=context
            )

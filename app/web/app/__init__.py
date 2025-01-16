from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.template.init import jinja

router = APIRouter()



@router.get("/", response_class=HTMLResponse, name="homepage")
def get_app_root(request: Request):

    return RedirectResponse(url=request.url_for("app_assessments_page"), status_code=301)
    

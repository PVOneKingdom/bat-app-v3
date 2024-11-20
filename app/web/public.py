from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.template.init import jinja


router = APIRouter()



@router.get("/", response_class=HTMLResponse, name="homepage")
def homepage_get(request: Request):
    
    context = {
            "request": request,
            }

    response = jinja.TemplateResponse(
            name="public/homepage.html",
            context=context,
            )

    return response


 
@router.get("/login", response_class=HTMLResponse, name="login_page")
def login_page_get(request: Request):
    
    context = {
            "request": request,
            }

    response = jinja.TemplateResponse(
            name="public/login.html",
            context=context,
            )

    return response

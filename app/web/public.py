from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.exception.database import RecordNotFound
from app.exception.service import IncorectCredentials
from app.model.user import UserLogin
from app.template.init import jinja
from app.service.auth import handle_token_creation


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


@router.post("/login", response_class=HTMLResponse)
def login_page_post(credentials: UserLogin, request: Request):

    context: dict = {
            "request": request,
            "focus_input_name": "username",
            }

    status_code = 200

    try:
        token = handle_token_creation(username=credentials.username, password=credentials.password)
        context["notification"] = 1
        context["notification_type"] = "success"
        context["notification_content"] = token
    except IncorectCredentials as e:
        context["notification"] = 1
        context["notification_type"] = "danger"
        context["notification_content"] = e.msg
        status_code = 401
    except RecordNotFound:
        context["notification"] = 1
        context["notification_type"] = "danger"
        context["notification_content"] = "Invalid credentials."
        status_code = 401
    except:
        context["notification"] = 1
        context["notification_type"] = "danger"
        context["notification_content"] = "Error occured."
        status_code = 401

    if credentials.username:
        context["username"] = credentials.username
        context["focus_input_name"] = "password"
        

    response = jinja.TemplateResponse(
            name="public/login.html",
            context=context,
            status_code=status_code
            )

    return response

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from app.exception.database import RecordNotFound
from app.exception.service import IncorectCredentials, InvalidBearerToken
from app.model.user import User, UserLogin
from app.template.init import jinja
from app.service.auth import handle_token_creation, auth_user, get_current_user

router = APIRouter()



@router.get("/", response_class=HTMLResponse, name="homepage")
def homepage_get(request: Request):
    
    context = {
            "title": "BAT App",
            "description": "Benchmark Assessment Tool.",
            "request": request,
            }

    response = jinja.TemplateResponse(
            name="public/homepage.html",
            context=context,
            )

    return response


@router.get("/logout", response_class=HTMLResponse, name="logout_page")
def logout_page_get(request: Request):

    context: dict = {
            "request": request,
            "title": "Logout",
            "description": "Logout from your current session.",
            }


    response = jinja.TemplateResponse(
            name="public/logout.html",
            context=context,
            )

    return response


@router.get("/token-check", name="token_check_endpoint")
def token_check_get(request: Request):

    token = request.headers.get("Authorization")
    data: dict = {}

    if not token:
        return HTTPException(status_code=401, detail="No access token appended")

    try:
        current_user: User = get_current_user(token.split(" ")[1]) # pyright: ignore
    except InvalidBearerToken as e:
        raise HTTPException(status_code=401, detail=e.msg)
    except RecordNotFound as e:
        raise HTTPException(status_code=401, detail=e.msg)

    user_role = current_user.role.value
    if user_role == "user":
        redirect_to = request.url_for("app_assessments_page")
    if user_role == "coach" or user_role == "admin":
        redirect_to = request.url_for("dashboard_assessments_page")

    return {"redirect_to":f"{redirect_to}"}

 
@router.get("/login", response_class=HTMLResponse, name="login_page")
def login_page_get(request: Request, expired_session: int = 0):
    
    context: dict = {
            "request": request,
            "title": "Login",
            "description": "Login to your BAT account.",
            }

    if expired_session == 1:
        context["notification"] = 1
        context["notification_type"] = "warning"
        context["notification_content"] = "Not logged in, or session expired. Log in again."

    response = jinja.TemplateResponse(
            name="public/login.html",
            context=context,
            )

    return response


@router.post("/login", response_class=HTMLResponse)
def login_page_post(credentials: UserLogin, request: Request):

    context: dict = {
            "title": "Login",
            "description": "Login to your BAT account.",
            "request": request,
            "focus_input_name": "username",
            }

    status_code = 200

    try:
        token = handle_token_creation(username=credentials.username, password=credentials.password)
        context["notification"] = 1
        context["notification_type"] = "success"
        context["notification_content"] = "Success! Redirecting."
        context["bearer_token"] = token

        current_user = auth_user(username=credentials.username, password=credentials.password)
        user_role = current_user.role.value
        if user_role == "user":
            context["redirect_to"] = request.url_for("app_assessments_page")
        if user_role == "coach" or user_role == "admin":
            context["redirect_to"] = request.url_for("dashboard_assessments_page")
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
        raise

    if credentials.username:
        context["username"] = credentials.username
        context["focus_input_name"] = "password"
        
    response = jinja.TemplateResponse(
            name="public/login.html",
            context=context,
            status_code=status_code
            )

    return response

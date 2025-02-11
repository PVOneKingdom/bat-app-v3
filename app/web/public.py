from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.config import CF_TURNSTILE_ENABLED, CF_TURNSTILE_SITE_KEY, SMTP_ENABLED

from app.exception.auth import CFTurnstileVerificationFailed
from app.exception.database import RecordNotFound
from app.exception.service import IncorectCredentials, InvalidBearerToken

from app.model.user import User, UserLogin, UserSetNewPassword
from app.model.emailreset import PasswordResetRequest


from app.template.init import jinja

from app.service import user as user_service
from app.service.auth import handle_token_creation, auth_user, get_current_user, \
        handle_token_renewal, user_htmx_dep, cf_verify_response

from app.web import prepare_notification



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
    """ Used for the purposes of determining whether or not
    user should be redirected to the login page or if we should pass
    user to the dash."""

    token = request.headers.get("Authorization")

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


@router.get("/password-reset", response_class=HTMLResponse, name="password_reset_page")
def get_password_reset(request: Request):

    context = {
            "request": request,
            "title": "Password Reset",
            "description": "Reset password for your account.",
            }

    # Disable password reset form when no SMTP is enabled
    if not SMTP_ENABLED:
        notification = prepare_notification(
                show=True,
                notification_type="warning",
                notification_content="Mail server not configured, ask your coach to reset password for you."
        )
        context.update(notification)

    response = jinja.TemplateResponse(
            name="public/password-reset.html",
            context=context,
            )

    return response
    
    

@router.post("/password-reset", response_class=HTMLResponse)
def post_password_reset(request: Request, email_reset_data: PasswordResetRequest):

    context = {
            "request": request,
            "title": "Password Reset",
            "description": "Reset password for your account.",
            }

    try:
        user_service.create_password_reset_token(email=email_reset_data.email, request=request)
        notification = prepare_notification(
                show=True,
                notification_type="success",
                notification_content="If email exists, we sent there reset link.")
        context.update(notification)
    except Exception as e:
        # NotImplemented
        pass

    response = jinja.TemplateResponse(
            name="public/password-reset.html",
            context=context,
            )

    return response



@router.get("/set-password", response_class=HTMLResponse, name="password_set_page")
def get_set_password(request: Request, reset_token: str | None = None):

    context = {
            "request": request,
            "title": "Set your password",
            "description": "Set password for your account.",
            "reset_token": reset_token,
            }

    if not reset_token:
        context.update(prepare_notification(True, "warning", "Token missing, invalid or missing try to request password reset again."))
    else:

        try:
            user: User = user_service.get_by_token(token=reset_token)
            context["user"] = user
            email_split = user.email.split("@")
            domain_part = email_split[-1].split(".")
            tld = domain_part[-1]
            context["concat_email"] = f"{email_split[0][0:2]}..{email_split[0][-2:]}@{email_split[1][0:2]}...{tld}"
        except RecordNotFound:
            context.update(prepare_notification(True, "warning", "Token missing, invalid or missing try to request password reset again."))

    response = jinja.TemplateResponse(
            name="public/password-set.html",
            context=context,
            )

    return response



@router.post("/set-password", response_class=HTMLResponse, name="password_set_page")
def post_set_password(request: Request, set_new_password: UserSetNewPassword):

    context = {
            "request": request,
            "title": "Set your password",
            "description": "Password set successfuly.",
            }

    try: 
        user = user_service.set_password_with_token(set_new_password=set_new_password)
        context["user"] = user
        context.update(prepare_notification(True, "success", f"Password for {user.username} has been set."))
    except Exception as e:
        # NotImplemented
        raise e

    response = jinja.TemplateResponse(
            name="public/password-set.html",
            context=context,
            )

    return response
    
    
@router.get("/token-renew", name="token_renew_endpoint")
def post_token_refresh(request: Request, current_user: User = Depends(user_htmx_dep)):

    new_token = handle_token_renewal(current_user=current_user)

    return {"access_token":new_token}

 
@router.get("/login", response_class=HTMLResponse, name="login_page")
def login_page_get(request: Request, expired_session: int = 0):
    
    context: dict = {
            "request": request,
            "title": "Login",
            "description": "Login to your BAT account.",
            }

    if CF_TURNSTILE_ENABLED:
        context["cf_turnstile_enabled"] = True
        context["cf_turnstile_site_key"] = CF_TURNSTILE_SITE_KEY

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

    context = {
            "title": "Login",
            "description": "Login to your BAT account.",
            "request": request,
            "focus_input_name": "username",
            }

    status_code = 200

    if CF_TURNSTILE_ENABLED:
        context["cf_turnstile_enabled"] = True
        context["cf_turnstile_site_key"] = CF_TURNSTILE_SITE_KEY

    try:
        if CF_TURNSTILE_ENABLED:
            cf_verification_passed = cf_verify_response(response=credentials.cf_turnstile_response)

        token = handle_token_creation(username=credentials.username, password=credentials.password)
        context["notification"] = 1
        context["notification_type"] = "success"
        context["notification_content"] = "Success! Redirecting."
        context["bearer_token"] = token

        current_user = auth_user(username=credentials.username, password=credentials.password)
        user_role = current_user.role.value
        context["token_manager_start"] = True
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
    except CFTurnstileVerificationFailed as e:
        context.update(prepare_notification(True, "danger", e.msg))
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

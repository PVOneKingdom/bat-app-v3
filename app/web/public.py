import os
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from time import sleep
from random import randrange

from app.config import CF_TURNSTILE_ENABLED, CF_TURNSTILE_SITE_KEY, SMTP_ENABLED

from app.exception.auth import CFTurnstileVerificationFailed
from app.exception.database import RecordNotFound
from app.exception.service import IncorectCredentials, InvalidBearerToken

from app.model.notification import Notification
from app.model.user import User, UserSetNewPassword
from app.model.emailreset import PasswordResetRequest


from app.template.init import jinja

from app.service import user as user_service
from app.service.authentication import (
    handle_token_creation,
    auth_user,
    get_current_user,
    handle_token_renewal,
    user_htmx_dep,
    cf_verify_response,
)


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
    """Used for the purposes of determining whether or not
    user should be redirected to the login page or if we should pass
    user to the dash."""

    token = request.cookies.get("access_token")

    if not token:
        return HTTPException(status_code=401, detail="No access token appended")

    try:
        current_user = get_current_user(token.split(" ")[1])
        if not current_user:
            raise RecordNotFound(msg="User was not found.")
    except InvalidBearerToken as e:
        raise HTTPException(status_code=401, detail=e.msg)
    except RecordNotFound as e:
        raise HTTPException(status_code=401, detail=e.msg)

    user_role = current_user.role.value
    redirect_to = None
    if user_role == "user":
        redirect_to = request.url_for("app_assessments_page")
    if user_role == "coach" or user_role == "admin":
        redirect_to = request.url_for("dashboard_assessments_page")

    return {"redirect_to": f"{redirect_to}"}


@router.get("/password-reset", response_class=HTMLResponse, name="password_reset_page")
def get_password_reset(request: Request):

    context = {
        "request": request,
        "title": "Password Reset",
        "description": "Reset password for your account.",
    }

    # Disable password reset form when no SMTP is enabled
    if not SMTP_ENABLED:
        context["notification"] = Notification(
            style="warning",
            content="Mail server not configured, ask your coach to reset password for you.",
        )

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
        user_service.create_password_reset_token(
            email=email_reset_data.email, request=request
        )
        context["notification"] = Notification(
            style="success", content="If email exists, we sent there reset link."
        )
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
        context["notification"] = Notification(
            style="warning",
            content="Token missing, invalid or missing try to request password reset again.",
        )
    else:

        try:
            user: User = user_service.get_by_token(token=reset_token)
            context["user"] = user
            email_split = user.email.split("@")
            domain_part = email_split[-1].split(".")
            tld = domain_part[-1]
            context["concat_email"] = (
                f"{email_split[0][0:2]}..{email_split[0][-2:]}@{email_split[1][0:2]}...{tld}"
            )
        except RecordNotFound:
            context["notification"] = Notification(
                style="warning",
                content="Token missing, invalid or missing try to request password reset again.",
            )
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
        context["notification"] = Notification(
            style="success", content=f"Password for {user.username} has been set."
        )
    except Exception as e:
        # NotImplemented
        raise e

    response = jinja.TemplateResponse(
        name="public/password-set.html",
        context=context,
    )

    return response


@router.get("/token-renew", name="token_renew_endpoint")
async def post_token_refresh(
    request: Request, current_user: User = Depends(user_htmx_dep)
):

    new_token = handle_token_renewal(current_user=current_user)

    return {"access_token": new_token}


@router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page_get(
    request: Request,
    notification: Notification | None = None,
    expired_session: int = 0,
    status_code: int | None = None,
):

    context: dict = {
        "request": request,
        "title": "Login",
        "description": "Login to your BAT account.",
    }

    if CF_TURNSTILE_ENABLED:
        context["cf_turnstile_enabled"] = True
        context["cf_turnstile_site_key"] = CF_TURNSTILE_SITE_KEY

    if expired_session:
        expired_notification = Notification(
            style="warning", content="Not logged in, or session expired. Log in again."
        )
        context["notification"] = expired_notification

    if notification:
        context["notification"] = notification

    response = jinja.TemplateResponse(
        name="public/login.html",
        context=context,
    )

    return response


@router.post("/login", response_class=HTMLResponse)
async def login_page_post(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    cf_token: Annotated[str | None, Form(alias="cf-turnstile-response")] = None,
    notification: str | None = None,
):
    context = {
        "title": "Login",
        "description": "Login to your BAT account.",
        "request": request,
        "focus_input_name": "username",
    }

    # Prevent information leaking through varying server response times
    delay = randrange(100, 500) / 1000
    sleep(delay)

    token = None

    status_code = 200

    if CF_TURNSTILE_ENABLED:
        context["cf_turnstile_enabled"] = True
        context["cf_turnstile_site_key"] = CF_TURNSTILE_SITE_KEY

    try:
        if CF_TURNSTILE_ENABLED:
            cf_verify_response(response=cf_token)

        # handle email logins
        if "@" in username:
            username = user_service.username_from_email(username)

        token = handle_token_creation(username=username, password=password)

        current_user = auth_user(username=username, password=password)
        user_role = current_user.role.value

        response = None

        if token and current_user and user_role:
            if user_role == "user":
                response = RedirectResponse(
                    status_code=303, url=request.url_for("app_assessments_page")
                )
            if user_role == "coach" or user_role == "admin":
                response = RedirectResponse(
                    status_code=303, url=request.url_for("dashboard_assessments_page")
                )

            if not response:
                raise IncorectCredentials(
                    msg="Incorrect credentials, unable to authenticate."
                )
            # Disable secure for non https - since cookies will be rejected on LAN IP's
            if os.getenv("FORCE_HTTPS_PATHS_ENV"):
                response.set_cookie(
                    key="access_token",
                    value=token,
                    httponly=True,
                    secure=True,
                    samesite="strict",
                )
            else:
                response.set_cookie(
                    key="access_token", value=token, httponly=True, samesite="strict"
                )

            return response

    except IncorectCredentials as e:
        notification = Notification(style="danger", content=e.msg)
        status_code = 401
    except RecordNotFound:
        notification = Notification(style="danger", content="Invalid credentials.")
        status_code = 401
    except CFTurnstileVerificationFailed as e:
        notification = Notification(style="danger", content=e.msg)
        status_code = 401
    except Exception as e:
        notification = Notification(style="danger", content=str(e))
        status_code = 401

    return await login_page_get(
        notification=notification, request=request, status_code=status_code
    )

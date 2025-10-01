from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from sqlite3 import IntegrityError

from app.exception.database import RecordNotFound, UsernameOrEmailNotUnique
from app.exception.service import SMTPCredentialsNotSet
from app.exception.service import (
    EndpointDataMismatch,
    InvalidFormEntry,
    SendingEmailFailed,
    Unauthorized,
)
from app.model.user import User, UserCreate, UserUpdate
from app.model.notification import Notification
from app.config import SMTP_ENABLED
from app.template.init import jinja
from app.service.authentication import user_htmx_dep
import app.service.user as service


router = APIRouter()

# -------------------------------------
# User management
# -------------------------------------


@router.get("", response_class=HTMLResponse, name="dashboard_users_page")
def get_users(request: Request, current_user: User = Depends(user_htmx_dep)):

    users = service.get_all(current_user)

    context = {
        "request": request,
        "title": "Users",
        "description": "List of users and their details.",
        "current_user": current_user,
        "users": users,
    }

    template_response = jinja.TemplateResponse(
        name="dashboard/users.html", context=context
    )

    return template_response


@router.get("/add", response_class=HTMLResponse, name="dashboard_user_add_page")
async def add_user(request: Request, current_user: User = Depends(user_htmx_dep)):

    context = {
        "request": request,
        "title": "Add User",
        "description": "BAT App dashboard interface",
        "available_roles": current_user.can_grant_roles(),
    }

    template_response = jinja.TemplateResponse(
        name="dashboard/user-create.html", context=context
    )

    return template_response


@router.post("/add", response_class=HTMLResponse)
async def add_user_post(
    request: Request, new_user: UserCreate, current_user: User = Depends(user_htmx_dep)
):

    context = {
        "request": request,
        "title": "Add User",
        "description": "BAT App dashboard interface",
        "available_roles": current_user.can_grant_roles(),
    }

    status_code: int = 201

    try:
        created_user: User = service.create(
            user=new_user, request=request, current_user=current_user
        )
        notification_content = f"User {created_user.username} created!"
        context["notification"] = Notification(
            style="success", content=notification_content
        )
    except SMTPCredentialsNotSet as e:
        context["notification"] = Notification(
            style="warning",
            content=e.msg,
        )
    except SendingEmailFailed as e:
        created_user = service.get_by_email(
            email=new_user.email, current_user=current_user
        )
        context["notification"] = Notification(
            style="warning",
            content=f"User {created_user.username} was created but email wasn't sent. Verify the credentials.",
        )
    except Unauthorized as e:
        context["notification"] = Notification(style="danger", content=e.msg)
        status_code = 401
    except UsernameOrEmailNotUnique as e:
        context["notification"] = Notification(style="warning", content=e.msg)
        status_code = 422
    except InvalidFormEntry as e:
        context["notification"] = Notification(style="warning", content=e.msg)
        status_code = 422

    template_response = jinja.TemplateResponse(
        name="dashboard/user-create.html", context=context, status_code=status_code
    )

    return template_response


@router.get("/{user_id}", response_class=HTMLResponse, name="dashboard_user_edit_page")
async def edit_user(
    user_id: str, request: Request, current_user: User = Depends(user_htmx_dep)
):

    try:
        user_for_edit: User = service.get(user_id=user_id, current_user=current_user)
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=e.msg)
    except Unauthorized as e:
        raise HTTPException(status_code=403, detail=e.msg)

    context = {
        "request": request,
        "title": f"Edit user: {user_for_edit.username}",
        "description": f"Edit details of the {user_for_edit.username}",
        "user_for_edit": user_for_edit,
        "available_roles": current_user.can_grant_roles(),
    }

    template_response = jinja.TemplateResponse(
        name="dashboard/user-edit.html", context=context
    )

    return template_response


@router.put("/{user_id}", response_class=HTMLResponse)
async def update_user(
    user_id: str,
    updated_user: UserUpdate,
    request: Request,
    current_user: User = Depends(user_htmx_dep),
):

    user_for_edit = service.get(user_id=user_id, current_user=current_user)

    context = {
        "request": request,
        "successful_update": True,
        "available_roles": current_user.can_grant_roles(),
        "user_for_edit": user_for_edit,
        "title": f"Edit user: {user_for_edit.username}",
        "description": f"Edit details of the {user_for_edit.username}",
    }

    status_code = 202

    try:
        edited_user: User = service.update(user_id, updated_user, current_user)
        context["user_for_edit"] = edited_user
        context["notification"] = Notification(
            style="success", content=f"User {edited_user.username} updated!"
        )
    except RecordNotFound as e:
        status_code = 404
        context["notification"] = Notification(style="warning", content=e.msg)
    except Unauthorized as e:
        status_code = 401
        context["notification"] = Notification(style="danger", content=e.msg)
    except EndpointDataMismatch as e:
        status_code = 403
        context["notification"] = Notification(style="danger", content=e.msg)
    except UsernameOrEmailNotUnique as e:
        status_code = 403
        context["notification"] = Notification(style="danger", content="")

    template_response = jinja.TemplateResponse(
        name="dashboard/user-edit.html", context=context, status_code=status_code
    )

    return template_response


@router.delete("/{user_id}", response_class=HTMLResponse)
async def delete_user(
    user_id: str, request: Request, current_user: User = Depends(user_htmx_dep)
):

    context = {
        "request": request,
        "title": "Users",
        "description": "List of users and their details.",
        "current_user": current_user,
    }

    try:
        deleted_user: User = service.delete(user_id, current_user)
        context["notification"] = Notification(
            style="success", content=f"User {deleted_user.username} was deleted."
        )
    except RecordNotFound as e:
        context["notification"] = Notification(style="warning", content=e.msg)
    except Unauthorized as e:
        context["notification"] = Notification(style="danger", content=e.msg)
    except IntegrityError as e:
        error_message = str(e).lower()
        if "FOREIGN KEY constraint failed".lower() in error_message:
            user = service.get(user_id=user_id, current_user=current_user)
            notifcation = Notification(
                style="warning",
                content=f"User {user.username} has still some resources attached. Try checking the assessments and reassigning them to someone else before deletion.",
            )
            context.update(notifcation)

    context["users"] = service.get_all(current_user=current_user)

    template_response = jinja.TemplateResponse(
        name="dashboard/users.html", context=context
    )

    return template_response

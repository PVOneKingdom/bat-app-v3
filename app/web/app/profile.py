from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.service.authentication import user_htmx_dep
from app.service import user as user_service
from app.template.init import jinja

from app.model.notification import Notification
from app.model.user import User, UserUpdate
from app.exception.database import RecordNotFound, UsernameOrEmailNotUnique
from app.exception.service import EndpointDataMismatch, Unauthorized


router = APIRouter()


# -------------------------------------
# Routes
# -------------------------------------


@router.get("", response_class=HTMLResponse, name="user_profile_page")
def get_profile(request: Request, current_user: User = Depends(user_htmx_dep)):

    context = {
        "request": request,
        "title": f"Edit your profile.",
        "description": f"Edit details of your profile.",
    }

    try:
        if current_user.user_id:
            user_for_edit: User = user_service.get(
                user_id=current_user.user_id, current_user=current_user
            )
            context["user_for_edit"] = user_for_edit
            context["available_roles"] = current_user.can_grant_roles()
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=e.msg)
    except Unauthorized as e:
        raise HTTPException(status_code=403, detail=e.msg)

    template_response = jinja.TemplateResponse(name="app/profile.html", context=context)

    return template_response


@router.put("", response_class=HTMLResponse)
def put_profile(
    request: Request,
    updated_user: UserUpdate,
    current_user: User = Depends(user_htmx_dep),
):

    context = {
        "request": request,
        "title": f"Edit your profile.",
        "description": f"Edit details of your profile.",
    }

    status_code = 202
    if current_user.user_id:
        user_for_edit = user_service.get(
            user_id=current_user.user_id, current_user=current_user
        )
        context.update(
            {
                "available_roles": current_user.can_grant_roles(),
                "user_for_edit": user_for_edit,
            }
        )
        try:
            edited_user: User = user_service.update(
                user_id=current_user.user_id,
                user=updated_user,
                current_user=current_user,
            )
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
            context["notification"] = Notification(style="danger", content=e.msg)

    template_response = jinja.TemplateResponse(
        name="app/profile.html", context=context, status_code=status_code
    )

    return template_response

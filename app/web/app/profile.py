from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from app.service.auth import user_htmx_dep
from app.service import user as user_service
from app.template.init import jinja

from app.model.user import User, UserUpdate
from app.exception.database import RecordNotFound
from app.exception.service import Unauthorized


router = APIRouter()


# -------------------------------------
# Routes
# -------------------------------------

@router.get("", response_class=HTMLResponse, name="user_profile_page")
def get_profile(request: Request, current_user: User = Depends(user_htmx_dep)):

    context = {
            "request": request,
            "title":f"Edit your profile.",
            "description":f"Edit details of your profile.",
            }

    try:
        if current_user.user_id:
            user_for_edit: User = user_service.get(user_id=current_user.user_id, current_user=current_user)
            context["user_for_edit"] = user_for_edit
            context["available_roles"] = current_user.can_grant_roles()
    except RecordNotFound as e:
        raise HTTPException(status_code=404, detail=e.msg)
    except Unauthorized as e:
        raise HTTPException(status_code=403, detail=e.msg)


    template_response = jinja.TemplateResponse(
            name="app/profile.html",
            context=context
            )

    return template_response


@router.put("", response_class=HTMLResponse)
def put_profile(request: Request, updated_user: UserUpdate, current_user: User = Depends(user_htmx_dep)):

    #NotImplemented
    return ""
    if current_user.user_id:
        user_for_edit = user_service.get(user_id=current_user.user_id, current_user=current_user)
        context = {
                "request": request,
                "successful_update": True,
                "available_roles": current_user.can_grant_roles(),
                "user_for_edit": user_for_edit,
                "title": f"Edit user: {user_for_edit.username}",
                "description": f"Edit details of the {user_for_edit.username}"
                }


    status_code = 202

    try:
        edited_user: User = service.update(user_id, updated_user, current_user)
        context["user_for_edit"] = edited_user
        context.update(prepare_notification(True, "success", f"User {edited_user.username} updated!"))
    except RecordNotFound as e:
        status_code = 404
        context.update(prepare_notification(True, "warning", e.msg))
    except Unauthorized as e:
        status_code = 401
        context.update(prepare_notification(True, "danger", e.msg))
    except EndpointDataMismatch as e:
        status_code = 403
        context.update(prepare_notification(True, "danger", e.msg))
    except UsernameOrEmailNotUnique as e:
        status_code = 403
        context.update(prepare_notification(True, "danger", e.msg))

    template_response = jinja.TemplateResponse(
            name="dashboard/user-edit.html",
            context=context,
            status_code=status_code
            )

    return template_response

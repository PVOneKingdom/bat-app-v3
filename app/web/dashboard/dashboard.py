from fastapi import APIRouter, Depends, Request

from app.template.init import jinja
from app.model.user import User
from app.service.authentication import user_htmx_dep


router = APIRouter()



@router.get("", name="dashboard")
def get_dashboard(request: Request, current_user: User = Depends(user_htmx_dep)):
    
    context = {
            "title": "Dasboard",
            "description": "Overview for navigating the tool.",
            "request": request,
            }

    response = jinja.TemplateResponse(
            name="dashboard/dashboard.html",
            context=context,
            )

    return response

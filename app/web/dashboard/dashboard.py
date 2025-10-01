from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.template.init import jinja
from app.model.user import User
from app.service.authentication import user_htmx_dep


router = APIRouter()


@router.get("", name="dashboard")
def get_dashboard(request: Request, current_user: User = Depends(user_htmx_dep)):

    return RedirectResponse(
        url=request.url_for("dashboard_assessments_page"), status_code=303
    )

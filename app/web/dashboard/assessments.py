from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.template.init import jinja
from app.model.user import User
from app.service.auth import user_htmx_dep
import app.service.assessment as service


router = APIRouter()


@router.get("", response_class=HTMLResponse, name="dashboard_assessments_page")
def get_assessments(request:Request, current_user: User = Depends(user_htmx_dep)):

    try:
        assessments = service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
            "request": request,
            "title":"Assessments",
            "description":"List of all available assessments.",
            "current_user": current_user,
            "assessments": assessments,
            }

    response = jinja.TemplateResponse(
            name="dashboard/assessments.html",
            context=context
            )

    return response


@router.get("/create", response_class=HTMLResponse, name="dashboard_assessment_create_page")
def get_assessment_create(request=Request, current_user: User = Depends(user_htmx_dep)):


    context = {
            "request": request,
            "title":"Create Assessment",
            "description":"Create new assessment.",
            "current_user": current_user,
            }


    response = jinja.TemplateResponse(
            name="dashboard/assessments-create.html",
            context=context
            )

    return response


@router.post("/create", response_class=HTMLResponse)
def post_assessment_create(request=Request, current_user: User = Depends(user_htmx_dep)):

    try:
        assessments = service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise


    context = {
            "request": request,
            "title":"Assessments",
            "description":"List of all available assessments.",
            "current_user": current_user,
            #"assessments": assessments,
            }


    response = jinja.TemplateResponse(
            name="dashboard/assessments.html",
            context=context
            )

    return response

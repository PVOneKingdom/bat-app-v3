from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.model.assesment import AssessmentPost
from app.template.init import jinja
from app.model.user import User
from app.service.auth import user_htmx_dep

import app.service.user as user_service
import app.service.assessment as service
from app.web import prepare_notification


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
def get_assessment_create(request: Request, current_user: User = Depends(user_htmx_dep)):

    try:
        users: list[User] = user_service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
            "request": request,
            "title":"Create Assessment",
            "description":"Create new assessment.",
            "users": users,
            "current_user": current_user,
            }


    response = jinja.TemplateResponse(
            name="dashboard/assessments-create.html",
            context=context
            )

    return response


@router.post("/create", response_class=HTMLResponse)
def post_assessment_create(assessment_new: AssessmentPost, request: Request, current_user: User = Depends(user_htmx_dep)):

    context = {
            "request": request,
            "title":"Create Assessment",
            "description":"Create new assessment.",
            "current_user": current_user,
            }

    try:
        service.create_assessment(assessment_post=assessment_new, current_user=current_user)
        users: list[User] = user_service.get_all(current_user=current_user)
        context.update(prepare_notification(True, "success", f"Assessment {assessment_new.assessment_name} successfully created."))
        context["users"] = user_service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise



    response = jinja.TemplateResponse(
            name="dashboard/assessments-create.html",
            context=context
            )

    return response


@router.get("/edit/{assessment_id}", response_class=HTMLResponse, name="dashboard_assessment_edit_page")
def get_assessment_edit(assessment_id: str, request:Request, current_user: User = Depends(user_htmx_dep)):

    return ""


@router.get("/{assessment_id}", response_class=HTMLResponse, name="dashboard_assessment_page")
def get_assessment(assessment_id: str, request:Request, current_user: User = Depends(user_htmx_dep)):

    try:
        assessment = service.get_assessment(assessment_id=assessment_id, current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
            "request": request,
            "title":"Assessment",
            "description":"Assessment detail page.",
            "current_user": current_user,
            "assessment": assessment,
            }

    response = jinja.TemplateResponse(
            name="dashboard/assessment-view.html",
            context=context
            )

    return response


@router.delete("/{assessment_id}", response_class=HTMLResponse)
def delete_assessment(assessment_id: str, request:Request, current_user: User = Depends(user_htmx_dep)):

    try:
        deleted_assessment = service.delete_assessment(assessment_id=assessment_id, current_user=current_user)
        assessments = service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
            "request": request,
            "title":"Assessment",
            "description":"Assessment detail page.",
            "current_user": current_user,
            "assessment": delete_assessment,
            "assessments": assessments
            }

    context.update(prepare_notification(True, "success", f"Assessment {deleted_assessment.assessment_name} removed!"))

    response = jinja.TemplateResponse(
            name="dashboard/assessments.html",
            context=context
            )

    return response

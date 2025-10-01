from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from typing import Annotated
import json

from app.data.note import get_note
from app.exception.service import EndpointDataMismatch, Unauthorized
from app.model.assesment import (
    AssessmentAnswerPost,
    AssessmentChown,
    AssessmentNote,
    AssessmentPost,
    AssessmentQA,
)
from app.template.init import jinja
from app.model.user import User
from app.model.notification import Notification
from app.service.authentication import user_htmx_dep

import app.service.user as user_service
import app.service.assessment as service
import app.service.note as note_service


router = APIRouter()


@router.get("", response_class=HTMLResponse, name="dashboard_assessments_page")
def get_assessments(request: Request, current_user: User = Depends(user_htmx_dep)):

    try:
        assessments = service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": "Assessments",
        "description": "List of all available assessments.",
        "current_user": current_user,
        "assessments": assessments,
    }

    response = jinja.TemplateResponse(
        name="dashboard/assessments.html", context=context
    )

    return response


@router.put("", response_class=HTMLResponse)
def put_assessments_chown(
    request: Request,
    assessment_chown: AssessmentChown,
    current_user: User = Depends(user_htmx_dep),
):

    try:
        service.chown(assessment_chown=assessment_chown, current_user=current_user)
        assessments = service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": "Assessments",
        "description": "List of all available assessments.",
        "current_user": current_user,
        "assessments": assessments,
    }

    response = jinja.TemplateResponse(
        name="dashboard/assessments.html", context=context
    )

    return response


@router.get(
    "/create", response_class=HTMLResponse, name="dashboard_assessment_create_page"
)
def get_assessment_create(
    request: Request, current_user: User = Depends(user_htmx_dep)
):

    try:
        users: list[User] = user_service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": "Create Assessment",
        "description": "Create new assessment.",
        "users": users,
        "current_user": current_user,
    }

    response = jinja.TemplateResponse(
        name="dashboard/assessment-create.html", context=context
    )

    return response


@router.post("/create", response_class=HTMLResponse)
def post_assessment_create(
    assessment_new: AssessmentPost,
    request: Request,
    current_user: User = Depends(user_htmx_dep),
):

    context = {
        "request": request,
        "title": "Create Assessment",
        "description": "Create new assessment.",
        "current_user": current_user,
    }

    try:
        service.create_assessment(
            assessment_post=assessment_new, current_user=current_user
        )
        users: list[User] = user_service.get_all(current_user=current_user)
        context["notification"] = Notification(
            style="success",
            content=f"Assessment {assessment_new.assessment_name} successfully created.",
        )
        context["users"] = user_service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        name="dashboard/assessment-create.html", context=context
    )

    return response


@router.get(
    "/edit/{assessment_id}",
    response_class=HTMLResponse,
    name="dashboard_assessment_edit_page",
)
def get_assessment_edit(
    request: Request, assessment_id: str, current_user: User = Depends(user_htmx_dep)
):

    context = {
        "request": request,
        "title": "Assessment Details",
        "description": "Assessment detail",
        "current_user": current_user,
    }

    try:
        assessment_qa: list[AssessmentQA] = service.get_all_qa(
            assessment_id=assessment_id, current_user=current_user
        )
        context["title"] = f"{assessment_qa[0].assessment_name}"
        context["assessment_qa"] = assessment_qa
        context["wheel"] = service.prepare_wheel_context(assessment_qa=assessment_qa)
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        name="dashboard/assessment-edit.html", context=context
    )

    return response


@router.get(
    "/edit/{assessment_id}/{category_order}/{question_order}",
    response_class=HTMLResponse,
    name="dashboard_assessment_answer_question_page",
)
def get_answer_question_page(
    request: Request,
    assessment_id: str,
    category_order: int,
    question_order: int,
    current_user: User = Depends(user_htmx_dep),
):

    context = {
        "request": request,
        "title": "Assessment Details",
        "description": "Assessment detail",
        "current_user": current_user,
        "assessment_id": assessment_id,
    }

    try:
        assessment_qa: list[AssessmentQA] = service.get_all_qa(
            assessment_id=assessment_id, current_user=current_user
        )
        current_question: AssessmentQA = (
            service.filter_assessment_qa_by_category_order_and_question_id(
                assessment_qa=assessment_qa,
                category_order=category_order,
                question_order=question_order,
            )
        )
        previous_question, next_question = service.get_neighbouring_questions(
            assessment_qa=assessment_qa,
            category_order=category_order,
            question_order=question_order,
        )

        context["assessment_qa"] = assessment_qa
        context["title"] = f"{assessment_qa[0].assessment_name}"
        context["current_question"] = current_question
        context["wheel"] = service.prepare_wheel_context(assessment_qa=assessment_qa)
        context["previous_question"] = previous_question
        context["next_question"] = next_question
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        name="dashboard/assessment-answer-question.html", context=context
    )

    return response


@router.post(
    "/edit/{assessment_id}/{category_order}/{question_order}",
    response_class=HTMLResponse,
)
def post_answer_question_page(
    answer_data: AssessmentAnswerPost,
    assessment_id: str,
    category_order: int,
    question_order: int,
    request: Request,
    current_user: User = Depends(user_htmx_dep),
):

    context = {
        "request": request,
        "title": "Assessment Details",
        "description": "Assessment detail",
        "current_user": current_user,
    }

    try:
        service.save_answer(answer_data=answer_data, current_user=current_user)
        assessment_qa: list[AssessmentQA] = service.get_all_qa(
            assessment_id=assessment_id, current_user=current_user
        )
        current_question: AssessmentQA = (
            service.filter_assessment_qa_by_category_order_and_question_id(
                assessment_qa=assessment_qa,
                category_order=category_order,
                question_order=question_order,
            )
        )
        previous_question, next_question = service.get_neighbouring_questions(
            assessment_qa=assessment_qa,
            category_order=category_order,
            question_order=question_order,
        )

        context["assessment_qa"] = assessment_qa
        context["title"] = f"{assessment_qa[0].assessment_name}"
        context["current_question"] = current_question
        context["wheel"] = service.prepare_wheel_context(assessment_qa=assessment_qa)
        context["previous_question"] = previous_question
        context["next_question"] = next_question
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        name="dashboard/assessment-answer-question.html", context=context
    )

    return response


@router.get(
    "/review/{assessment_id}/",
    response_class=HTMLResponse,
    name="dashboard_assessment_review_page",
)
def get_answer_question_review_page(
    request: Request, assessment_id: str, current_user: User = Depends(user_htmx_dep)
):

    context = {
        "request": request,
        "title": "View Assessment",
        "description": "View assessment",
        "current_user": current_user,
        "assessment_id": assessment_id,
    }

    try:
        assessment_qa: list[AssessmentQA] = service.get_all_qa(
            assessment_id=assessment_id, current_user=current_user
        )

        context["assessment_qa"] = assessment_qa
        context["title"] = f"{assessment_qa[0].assessment_name}"
        context["wheel"] = service.prepare_wheel_context(assessment_qa=assessment_qa)
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        name="dashboard/assessment-review.html", context=context
    )

    return response


@router.get(
    "/review/{assessment_id}/{category_order}",
    response_class=HTMLResponse,
    name="dashboard_assessment_category_review_page",
)
def get_answer_question_category_review_page(
    assessment_id: str,
    category_order: int,
    request: Request,
    current_user: User = Depends(user_htmx_dep),
):

    context = {
        "request": request,
        "title": "View Assessment",
        "description": "View assessment",
        "current_user": current_user,
        "assessment_id": assessment_id,
        "current_category_order": category_order,
    }

    try:
        assessment_qa: list[AssessmentQA] = service.get_all_qa(
            assessment_id=assessment_id, current_user=current_user
        )

        assessment_category_qa: list[AssessmentQA] = (
            service.filter_assessment_qa_by_category(
                assessment_qa=assessment_qa, category_order=category_order
            )
        )

        assessment_category_note: AssessmentNote = note_service.get_note(
            assessment_id=assessment_id,
            category_order=category_order,
            current_user=current_user,
        )

        previous_category, next_category = service.get_neighbouring_categories_number(
            category_order=category_order
        )

        context["previous_category"] = previous_category
        context["next_category"] = next_category
        context["assessment_qa"] = assessment_qa
        context["assessment_category_qa"] = assessment_category_qa
        context["assessment_category_note"] = assessment_category_note
        context["title"] = f"{assessment_qa[0].assessment_name}"
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        name="dashboard/assessment-category-review.html", context=context
    )

    return response


@router.put("/review/{assessment_id}/{category_order}", response_class=HTMLResponse)
def put_answer_question_category_review_page(
    request: Request,
    assessment_id: str,
    category_order: int,
    assessment_note: AssessmentNote,
    current_user: User = Depends(user_htmx_dep),
):

    context = {
        "request": request,
        "title": "View Assessment",
        "description": "View assessment",
        "current_user": current_user,
        "assessment_id": assessment_id,
        "current_category_order": category_order,
    }

    try:
        note_service.update_note(
            assessment_note=assessment_note, current_user=current_user
        )
    except:
        raise

    try:
        assessment_qa: list[AssessmentQA] = service.get_all_qa(
            assessment_id=assessment_id, current_user=current_user
        )

        assessment_category_qa: list[AssessmentQA] = (
            service.filter_assessment_qa_by_category(
                assessment_qa=assessment_qa, category_order=category_order
            )
        )

        assessment_category_note: AssessmentNote = note_service.get_note(
            assessment_id=assessment_id,
            category_order=category_order,
            current_user=current_user,
        )

        previous_category, next_category = service.get_neighbouring_categories_number(
            category_order=category_order
        )

        context["previous_category"] = previous_category
        context["next_category"] = next_category

        context["assessment_qa"] = assessment_qa
        context["assessment_category_qa"] = assessment_category_qa
        context["assessment_category_note"] = assessment_category_note
        context["title"] = f"{assessment_qa[0].assessment_name}"
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        name="dashboard/assessment-category-review.html", context=context
    )

    return response


@router.get(
    "/{assessment_id}", response_class=HTMLResponse, name="dashboard_assessment_page"
)
def get_assessment(
    assessment_id: str, request: Request, current_user: User = Depends(user_htmx_dep)
):

    try:
        assessment = service.get_assessment(
            assessment_id=assessment_id, current_user=current_user
        )
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": "Assessment",
        "description": "Assessment detail page.",
        "current_user": current_user,
        "assessment": assessment,
    }

    response = jinja.TemplateResponse(
        name="dashboard/assessment-view.html", context=context
    )

    return response


@router.delete("/{assessment_id}", response_class=HTMLResponse)
def delete_assessment(
    assessment_id: str, request: Request, current_user: User = Depends(user_htmx_dep)
):

    try:
        deleted_assessment = service.delete_assessment(
            assessment_id=assessment_id, current_user=current_user
        )
        assessments = service.get_all(current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": "Assessment",
        "description": "Assessment detail page.",
        "current_user": current_user,
        "assessment": delete_assessment,
        "assessments": assessments,
    }

    context["notification"] = Notification(
        style="success",
        content=f"Assessment {deleted_assessment.assessment_name} removed!",
    )

    response = jinja.TemplateResponse(
        name="dashboard/assessments.html", context=context
    )

    return response


@router.get(
    "/chown/{assessment_id}",
    response_class=HTMLResponse,
    name="dashboard_assessment_chown",
)
def get_assessment_chown_for(
    request: Request, assessment_id: str, current_user: User = Depends(user_htmx_dep)
):

    try:
        users = user_service.get_all(current_user=current_user)
        assessment = service.get_assessment(
            assessment_id=assessment_id, current_user=current_user
        )
    except Unauthorized as e:
        raise e

    context = {
        "request": request,
        "users": users,
        "assessment_id": assessment_id,
        "assessment": assessment,
    }

    response = jinja.TemplateResponse(
        name="dashboard/assessments-change-owner.html", context=context
    )

    return response


@router.get(
    "/rename/{assessment_id}",
    response_class=HTMLResponse,
    name="dashboard_assessment_rename",
)
def get_assessment_rename_for(
    request: Request, assessment_id: str, current_user: User = Depends(user_htmx_dep)
):

    try:
        assessment = service.get_assessment(
            assessment_id=assessment_id, current_user=current_user
        )
    except Unauthorized as e:
        raise e

    context = {
        "request": request,
        "assessment_id": assessment_id,
        "assessment": assessment,
    }

    response = jinja.TemplateResponse(
        name="dashboard/assessments-rename.html", context=context
    )

    return response


@router.put(
    "/rename/{assessment_id}",
    response_class=HTMLResponse,
    name="dashboard_assessment_rename",
)
def put_assessment_rename_for(
    request: Request,
    assessment_id: str,
    form_assessment_id: Annotated[str, Form()],
    form_assessment_name: Annotated[str, Form()],
    current_user: User = Depends(user_htmx_dep),
):

    if assessment_id != form_assessment_id:
        raise EndpointDataMismatch(
            msg="Assessment id from URL does not match assessment id from form. Refresh page and try again."
        )

    try:
        response = service.rename(
            assessment_id=assessment_id,
            new_name=form_assessment_name,
            current_user=current_user,
        )
    except Unauthorized as e:
        raise e

    return get_assessments(request=request, current_user=current_user)

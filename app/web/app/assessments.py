from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.model.assesment import AssessmentAnswerPost, AssessmentQA
from app.model.user import User
import app.service.assessment as service
from app.service.authentication import user_htmx_dep
from app.template.init import jinja

from app.service import report as report_service


router = APIRouter()


@router.get("", response_class=HTMLResponse, name="app_assessments_page")
def get_assessments(request:Request, current_user: User = Depends(user_htmx_dep)):

    try:
        assessments = service.get_all_for_user(current_user=current_user)
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
            name="app/assessments.html",
            context=context
            )

    return response


@router.get("/edit/{assessment_id}", response_class=HTMLResponse, name="app_assessment_edit_page")
def get_assessment_edit(assessment_id: str, request:Request, current_user: User = Depends(user_htmx_dep)):

    context = {
            "request": request,
            "title":"Assessment Details",
            "description":"Assessment detail",
            "current_user": current_user,
            }

    try:
        assessment_qa: list[AssessmentQA] = service.get_all_qa(assessment_id=assessment_id, current_user=current_user)
        context["title"] = f"{assessment_qa[0].assessment_name}"
        context["assessment_qa"] = assessment_qa
        context["wheel"] = service.prepare_wheel_context(assessment_qa=assessment_qa)
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
            name="app/assessment-edit.html",
            context=context
            )

    return response


@router.get("/edit/{assessment_id}/{category_order}/{question_order}", response_class=HTMLResponse, name="app_assessment_answer_question_page")
def get_answer_question_page(assessment_id: str, category_order: int, question_order: int,  request:Request, current_user: User = Depends(user_htmx_dep)):

    context = {
            "request": request,
            "title":"Assessment Details",
            "description":"Assessment detail",
            "current_user": current_user,
            }

    try:
        assessment_qa: list[AssessmentQA] = service.get_all_qa(assessment_id=assessment_id, current_user=current_user)
        current_question: AssessmentQA = service.filter_assessment_qa_by_category_order_and_question_id(assessment_qa=assessment_qa, category_order=category_order, question_order=question_order)
        previous_question, next_question = service.get_neighbouring_questions(assessment_qa=assessment_qa, category_order=category_order, question_order=question_order)

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
            name="app/assessment-answer-question.html",
            context=context
            )

    return response


@router.post("/edit/{assessment_id}/{category_order}/{question_order}", response_class=HTMLResponse)
def post_answer_question_page(answer_data: AssessmentAnswerPost, assessment_id: str, category_order: int, question_order: int,  request:Request, current_user: User = Depends(user_htmx_dep)):

    context = {
            "request": request,
            "title":"Assessment Details",
            "description":"Assessment detail",
            "current_user": current_user,
            }

    try:
        service.save_answer(answer_data=answer_data, current_user=current_user)
        assessment_qa: list[AssessmentQA] = service.get_all_qa(assessment_id=assessment_id, current_user=current_user)
        current_question: AssessmentQA = service.filter_assessment_qa_by_category_order_and_question_id(assessment_qa=assessment_qa, category_order=category_order, question_order=question_order)
        previous_question, next_question = service.get_neighbouring_questions(assessment_qa=assessment_qa, category_order=category_order, question_order=question_order)

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
            name="app/assessment-answer-question.html",
            context=context
            )

    return response


@router.get("/{assessment_id}", response_class=HTMLResponse, name="app_assessment_page")
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
            name="app/assessment-view.html",
            context=context
            )

    return response



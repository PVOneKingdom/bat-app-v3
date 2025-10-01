from fastapi import APIRouter, Depends, Request, Response
from app.template.init import jinja
from fastapi.responses import HTMLResponse
from app.model.notification import Notification
from app.model.question import (
    Question,
    QuestionCategory,
    QuestionCategoryRename,
    QuestionCategoryReorder,
    QuestionEditContent,
)
from app.model.user import User
from app.service import question as service
from app.service.authentication import user_htmx_dep


router = APIRouter()


@router.get("", response_class=HTMLResponse, name="dashboard_questions_page")
def get_questions(request: Request, current_user: User = Depends(user_htmx_dep)):

    questions_categories: list[QuestionCategory] = service.get_all_categories(
        current_user=current_user
    )

    context = {
        "request": request,
        "title": "Questions",
        "description": "Manage questions and their order.",
        "current_user": current_user,
        "questions_categories": questions_categories,
    }

    response = jinja.TemplateResponse(context=context, name="dashboard/questions.html")

    return response


@router.get(
    "/reorder",
    response_class=HTMLResponse,
    name="dashboard_questions_reorder_category_page",
)
def get_questions_reorder_category(
    request: Request, current_user: User = Depends(user_htmx_dep)
):

    try:
        questions_categories: list[QuestionCategory] = service.get_all_categories(
            current_user=current_user
        )
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": "Reorder Categories",
        "description": "Reorder question categories.",
        "current_user": current_user,
        "questions_categories": questions_categories,
    }

    response = jinja.TemplateResponse(
        name="dashboard/questions-reorder.html", context=context
    )

    return response


@router.post("/reorder", response_class=HTMLResponse)
def post_questions_reorder_category(
    category_new_order: QuestionCategoryReorder,
    request: Request,
    current_user: User = Depends(user_htmx_dep),
):

    try:
        service.reorder_questions_category(
            questions_category_reorder=category_new_order, current_user=current_user
        )
    except:
        raise
    return ""


@router.get(
    "/{category_id}/rename",
    response_class=HTMLResponse,
    name="dashboard_question_category_rename_page",
)
def get_question_category_rename(
    category_id: int, request: Request, current_user: User = Depends(user_htmx_dep)
):

    questions_categories: list[QuestionCategory] = service.get_all_categories(
        current_user=current_user
    )
    questions_in_category: list[Question] = service.get_all_questions_for_category(
        category_id=category_id, current_user=current_user
    )
    category_for_edit: QuestionCategory = service.get_questions_category(
        category_id=category_id, current_user=current_user
    )

    context = {
        "request": request,
        "title": "Questions",
        "description": "Manage questions and their order.",
        "current_user": current_user,
        "current_category_id": category_id,
        "current_category_name": questions_in_category[0].category_name,
        "questions_in_category": questions_in_category,
        "questions_categories": questions_categories,
        "category_for_edit": category_for_edit,
    }

    response = jinja.TemplateResponse(
        context=context, name="dashboard/questions-rename.html"
    )

    return response


@router.post("/{category_id}/rename", response_class=HTMLResponse)
def post_question_category_rename(
    category_id: int,
    category_rename: QuestionCategoryRename,
    request: Request,
    response: Response,
    current_user: User = Depends(user_htmx_dep),
):

    try:
        service.rename_questions_category(
            category_id_from_path=category_id,
            category_rename=category_rename,
            current_user=current_user,
        )
    except:
        # NotImplemented
        raise

    dashboard_questions_page = request.url_for("dashboard_questions_page")

    response.status_code = 201
    response.headers["HX-Location"] = f"{dashboard_questions_page}/{category_id}"
    response.headers["HX-Push-Url"] = "true"
    response.headers["HX-Select"] = ".bat-body"
    response.headers["HX-Target"] = ".bat-body"
    response.headers["HX-Swap"] = "outerHTML"

    return response


@router.get("/{category_id}/{question_id}", response_class=HTMLResponse)
def get_question_category_page(
    category_id: int,
    question_id: int,
    request: Request,
    current_user: User = Depends(user_htmx_dep),
):

    try:
        questions_categories: list[QuestionCategory] = service.get_all_categories(
            current_user=current_user
        )
        question_for_editting: Question = service.get_one(
            question_id=question_id, current_user=current_user
        )
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": "Questions",
        "description": "Manage questions and their order.",
        "current_user": current_user,
        "questions_categories": questions_categories,
        "question_for_editting": question_for_editting,
    }

    response = jinja.TemplateResponse(
        context=context, name="dashboard/question-edit.html"
    )

    return response


@router.put("/{category_id}/{question_id}", response_class=HTMLResponse)
def put_question_category_page(
    category_id: int,
    question_id: int,
    question_edit_content: QuestionEditContent,
    request: Request,
    current_user: User = Depends(user_htmx_dep),
):

    context = {
        "request": request,
        "title": "Questions",
        "description": "Manage questions and their order.",
        "current_user": current_user,
    }

    try:
        questions_categories: list[QuestionCategory] = service.get_all_categories(
            current_user=current_user
        )
        question_for_editting: Question = service.update_question_content(
            question_edit_content=question_edit_content, current_user=current_user
        )
        context.update(
            {
                "questions_categories": questions_categories,
                "question_for_editting": question_for_editting,
            }
        )
        context["notification"] = Notification(
            style="success", content="Question updated"
        )
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        context=context, name="dashboard/question-edit.html"
    )

    return response


@router.get(
    "/{category_id}",
    response_class=HTMLResponse,
    name="dashboard_question_category_page",
)
def get_question_category_page(
    category_id: int, request: Request, current_user: User = Depends(user_htmx_dep)
):

    questions_categories: list[QuestionCategory] = service.get_all_categories(
        current_user=current_user
    )
    questions_in_category: list[Question] = service.get_all_questions_for_category(
        category_id=category_id, current_user=current_user
    )

    context = {
        "request": request,
        "title": "Questions",
        "description": "Manage questions and their order.",
        "current_user": current_user,
        "current_category_id": category_id,
        "current_category_name": questions_in_category[0].category_name,
        "questions_in_category": questions_in_category,
        "questions_categories": questions_categories,
    }

    response = jinja.TemplateResponse(
        context=context, name="dashboard/questions-list.html"
    )

    return response

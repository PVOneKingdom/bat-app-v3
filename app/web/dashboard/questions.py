from fastapi import APIRouter, Depends, Request
from app.template.init import jinja
from fastapi.responses import HTMLResponse
from app.model.question import Question, QuestionCategory
from app.model.user import User
from app.service import question as service
from app.service.auth import user_htmx_dep


router = APIRouter()

@router.get("", response_class=HTMLResponse, name="dashboard_questions_page")
def get_questions(request: Request, current_user: User = Depends(user_htmx_dep)):

    questions_categories: list[QuestionCategory] = service.get_all_categories(current_user=current_user)
    
    context = {
            "request": request,
            "title":"Questions",
            "description":"Manage questions and their order.",
            "current_user": current_user,
            "questions_categories": questions_categories
            }

    response = jinja.TemplateResponse(
            context=context,
            name="dashboard/questions.html"
            )

    return response


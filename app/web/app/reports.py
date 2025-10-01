from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.model.user import User
from app.service.authentication import user_htmx_dep
from app.template.init import jinja

from app.service import report as service
from app.service import assessment as assessment_service


router = APIRouter()


@router.get("", name="app_reports_root_page")
def get_reports(
    request: Request,
    assessment_filter: str | None = None,
    current_user: User = Depends(user_htmx_dep),
):

    return RedirectResponse(
        url=request.url_for("app_assessments_page"), status_code=301
    )


@router.get(
    "/{assessment_id}", response_class=HTMLResponse, name="app_reports_for_assessment"
)
def get_reports_for_assessment(
    request: Request, assessment_id: str, current_user: User = Depends(user_htmx_dep)
):

    assessment = assessment_service.get_for_user(
        assessment_id=assessment_id, current_user=current_user
    )
    reports = service.get_public_reports_for_assessment(
        assessment_id=assessment_id, current_user=current_user
    )

    context = {
        "request": request,
        "title": f"Reports for {assessment.assessment_name}",
        "description": f"List of all available reports for {assessment.assessment_name}",
        "current_user": current_user,
        "reports": reports,
        "assessment": assessment,
    }

    response = jinja.TemplateResponse(context=context, name="app/reports.html")

    return response


@router.get(
    "/view/{report_id}", response_class=HTMLResponse, name="app_report_view_page"
)
def get_report_view(
    request: Request, report_id: str, current_user: User = Depends(user_htmx_dep)
):

    try:
        report = service.get_public_report_for_user(
            report_id=report_id, current_user=current_user
        )
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": report.report_name,
        "report": report,
    }

    response = jinja.TemplateResponse(context=context, name="app/report-preview.html")

    return response

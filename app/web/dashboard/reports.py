from fastapi import APIRouter, Depends, Request

from app.model.report import Report, ReportCreate, ReportExtended
from app.service import report as service
from app.service import assessment as assessment_service

from app.model.user import User
from app.model.assesment import Assessment
from app.template.init import jinja
from fastapi.responses import HTMLResponse
from app.service.auth import user_htmx_dep
from app.web import prepare_notification


router = APIRouter()



@router.get("", response_class=HTMLResponse, name="dashboard_reports_page")
def get_questions(request: Request, current_user: User = Depends(user_htmx_dep)):

    reports_extended: list[ReportExtended] = service.get_all_extended(current_user=current_user)
    assessments: list[Assessment] = assessment_service.get_all(current_user=current_user)
    
    context = {
            "request": request,
            "title":"Reports",
            "description":"List of all available reports.",
            "current_user": current_user,
            "reports": reports_extended,
            "assessments": assessments
            }

    response = jinja.TemplateResponse(
            context=context,
            name="dashboard/reports.html"
            )

    return response


@router.get("/create", response_class=HTMLResponse, name="dashboard_report_create_page")
def get_report_create(request: Request, current_user: User = Depends(user_htmx_dep)):

    assessments: list[Assessment] = assessment_service.get_all(current_user=current_user)

    context = {
            "request": request,
            "title":"Create report",
            "description":"Create new report for existing assessment.",
            "current_user": current_user,
            "assessments":assessments,
            }

    response = jinja.TemplateResponse(
            context=context,
            name="dashboard/report-create.html"
            )

    return response


@router.post("/create", response_class=HTMLResponse)
def post_report_create(request: Request, report_create: ReportCreate, current_user: User = Depends(user_htmx_dep)):

    assessments: list[Assessment] = assessment_service.get_all(current_user=current_user)

    context = {
            "request": request,
            "title":"Create report",
            "description":"Create new report for existing assessment.",
            "current_user": current_user,
            "assessments":assessments,
            }

    try:
        report = service.create_report(report_create=report_create, current_user=current_user)
        context.update(prepare_notification(True, "success", f"Report {report.report_name} was created."))
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
            context=context,
            name="dashboard/report-create.html"
            )

    return response


@router.get("/edit/{report_id}", response_class=HTMLResponse, name="dashboard_report_edit_page")
def get_report_edit(request: Request, report_id: str, current_user: User = Depends(user_htmx_dep)):

    return


@router.post("/edit/{report_id}", response_class=HTMLResponse)
def post_report_edit(request: Request, report_id: str, report: Report, current_user: User = Depends(user_htmx_dep)):

    return



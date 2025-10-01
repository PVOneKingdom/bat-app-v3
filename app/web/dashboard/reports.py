from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.exception.service import SendingEmailFailed, Unauthorized
from app.service import report as service
from app.service import assessment as assessment_service
from app.service import note as note_service
from app.service import mail as mail_service

from app.model.report import ReportCreate, ReportExtended, ReportUpdate
from app.model.notification import Notification
from app.model.user import User
from app.model.assesment import Assessment

from app.template.init import jinja

from app.service.authentication import user_htmx_dep


router = APIRouter()


@router.get("", response_class=HTMLResponse, name="dashboard_reports_page")
def get_reports(
    request: Request,
    assessment_filter: str | None = None,
    current_user: User = Depends(user_htmx_dep),
    extra_notification=None,
):

    reports_extended: list[ReportExtended] = service.get_all_extended(
        current_user=current_user
    )
    assessments: list[Assessment] = assessment_service.get_all(
        current_user=current_user
    )

    if assessment_filter:
        reports_filtered = list(
            filter(
                lambda report: report.assessment_id == assessment_filter,
                reports_extended,
            )
        )
        reports_extended = reports_filtered

    context = {
        "request": request,
        "title": "Reports",
        "description": "List of all available reports.",
        "current_user": current_user,
        "reports": reports_extended,
        "assessments": assessments,
    }

    if extra_notification:
        context.update(extra_notification)

    response = jinja.TemplateResponse(context=context, name="dashboard/reports.html")

    return response


@router.get("/create", response_class=HTMLResponse, name="dashboard_report_create_page")
def get_report_create(request: Request, current_user: User = Depends(user_htmx_dep)):

    assessments: list[Assessment] = assessment_service.get_all(
        current_user=current_user
    )

    context = {
        "request": request,
        "title": "Create report",
        "description": "Create new report for existing assessment.",
        "current_user": current_user,
        "assessments": assessments,
    }

    response = jinja.TemplateResponse(
        context=context, name="dashboard/report-create.html"
    )

    return response


@router.post("/create", response_class=HTMLResponse)
def post_report_create(
    request: Request,
    report_create: ReportCreate,
    current_user: User = Depends(user_htmx_dep),
):

    assessments: list[Assessment] = assessment_service.get_all(
        current_user=current_user
    )

    context = {
        "request": request,
        "title": "Create report",
        "description": "Create new report for existing assessment.",
        "current_user": current_user,
        "assessments": assessments,
    }

    try:
        report = service.create_report(
            report_create=report_create, current_user=current_user
        )
        context["notification"] = Notification(
            style="success", content=f"Report {report.report_name} was created."
        )
    except:
        # NotImplemented
        raise

    response = jinja.TemplateResponse(
        context=context, name="dashboard/report-create.html"
    )

    return response


@router.get(
    "/edit/{report_id}", response_class=HTMLResponse, name="dashboard_report_edit_page"
)
def get_report_edit(
    request: Request, report_id: str, current_user: User = Depends(user_htmx_dep)
):

    try:
        report = service.get_report_extended(
            report_id=report_id, current_user=current_user
        )
        assessment_notes = note_service.get_assessment_notes(
            assessment_id=report.assessment_id, current_user=current_user
        )
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "report": report,
        "assessment_notes": assessment_notes,
        "title": "Edit report",
        "description": "Edit report and fill in the info.",
        "current_user": current_user,
    }

    response = jinja.TemplateResponse(
        context=context, name="dashboard/report-edit.html"
    )

    return response


@router.post("/edit/{report_id}", response_class=HTMLResponse)
def post_report_edit(
    request: Request,
    report_id: str,
    report_update: ReportUpdate,
    current_user: User = Depends(user_htmx_dep),
):

    try:
        service.update_report(
            report_id=report_id, report_update=report_update, current_user=current_user
        )
        report = service.get_report_extended(
            report_id=report_id, current_user=current_user
        )
        assessment_notes = note_service.get_assessment_notes(
            assessment_id=report.assessment_id, current_user=current_user
        )
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "report": report,
        "assessment_notes": assessment_notes,
        "title": "Edit report",
        "description": "Edit report and fill in the info.",
        "current_user": current_user,
    }

    response = jinja.TemplateResponse(
        context=context, name="dashboard/report-edit.html"
    )

    return response


@router.patch(
    "/publish/{report_id}/{public}",
    response_class=HTMLResponse,
    name="dashboard_report_publish",
)
def patch_report_publish_status(
    request: Request,
    report_id: str,
    public: bool,
    current_user: User = Depends(user_htmx_dep),
):

    try:
        report = service.publish_report(
            report_id=report_id, public=public, current_user=current_user
        )
        report_extended = service.extend_report(
            report=report, current_user=current_user
        )
    except Unauthorized as e:
        # NotImplemented
        raise

    context = {"request": request, "report": report_extended}

    response = jinja.TemplateResponse(
        context=context, name="dashboard/report-cell.html"
    )

    return response


@router.delete(
    "/{report_id}", response_class=HTMLResponse, name="dashboard_report_delete_page"
)
def delete_report(
    request: Request, report_id: str, current_user: User = Depends(user_htmx_dep)
):

    try:
        report_deleted = service.delete_report(
            report_id=report_id, current_user=current_user
        )
    except Unauthorized:
        # NotImplemented
        raise

    reports_extended: list[ReportExtended] = service.get_all_extended(
        current_user=current_user
    )
    assessments: list[Assessment] = assessment_service.get_all(
        current_user=current_user
    )

    context = {
        "request": request,
        "title": "Reports",
        "description": "List of all available reports.",
        "current_user": current_user,
        "reports": reports_extended,
        "assessments": assessments,
    }

    response = jinja.TemplateResponse(context=context, name="dashboard/reports.html")

    return response


@router.get(
    "/preview/{report_id}",
    response_class=HTMLResponse,
    name="dashboard_report_preview_page",
)
def get_report_preview(
    request: Request, report_id: str, current_user: User = Depends(user_htmx_dep)
):

    try:
        report = service.get_report(report_id=report_id, current_user=current_user)
    except:
        # NotImplemented
        raise

    context = {
        "request": request,
        "title": report.report_name,
        "report": report,
    }

    response = jinja.TemplateResponse(
        context=context, name="dashboard/report-preview.html"
    )

    return response


@router.get(
    "/notify-user/{report_id}",
    response_class=HTMLResponse,
    name="dashboard_report_notify_user",
)
def get_report_notify_user(
    request: Request,
    report_id: str,
    assessment_filter: str | None = None,
    current_user: User = Depends(user_htmx_dep),
):

    try:
        report_extended: ReportExtended = service.get_report_extended(
            report_id=report_id, current_user=current_user
        )
        mail_service.notify_report_published(
            report=report_extended, request=request, current_user=current_user
        )
        notification = Notification(
            style="success",
            content=f"User: {report_extended.assessment_owner} was notified about the report.",
        )
    except SendingEmailFailed as e:
        notification = Notification(
            style="danger",
            content=f"There was an error sending the e-mail. Check your mailserver credentials.",
        )

    return get_reports(
        request=request,
        assessment_filter=assessment_filter,
        current_user=current_user,
        extra_notification=notification,
    )

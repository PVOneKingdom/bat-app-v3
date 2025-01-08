import uuid
import secrets
from app.data import report as data
from app.model.report import Report, ReportCreate
from app.model.user import User
from app.exception.service import EndpointDataMismatch, Unauthorized


# -------------------------------
#   CRUD
# -------------------------------

def get_all(current_user: User) -> list[Report]:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    return data.get_all_reports()


def get_report(report_id: str, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    return data.get_report(report_id=report_id)


def update_report(report_id: str, report: Report, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    if not report_id == report.report_id:
        raise EndpointDataMismatch(msg="Provided report object doesn't match endpoint ID.")

    return data.update_report(report=report)


def delete_report(report_id: str, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    return data.get_report(report_id=report_id)

def create_report(report_create: ReportCreate, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    report = Report(
            report_id=str(uuid.uuid4()),
            report_name=report_create.report_name,
            assessment_id=report_create.assessment_id,
            public=False,
            key=secrets.token_urlsafe(16),
            summary=None,
            recommendation_title_1=None,
            recommendation_content_1=None,
            recommendation_title_2=None,
            recommendation_content_2=None,
            recommendation_title_3=None,
            recommendation_content_3=None,
            )

    return data.create_report(report=report)

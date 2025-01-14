import uuid
import secrets



from app.data import report as data
from app.model.assesment import Assessment
from app.service import assessment as assessment_service
from app.model.report import Report, ReportCreate, ReportExtended
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

    return data.delete_report(report_id=report_id)

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


def publish_report(report_id: str, public: bool, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    return data.publish_report(report_id=report_id, public=public)



def get_all_extended(current_user: User) -> list[ReportExtended]:

    all_reports: list[Report] = get_all(current_user=current_user)

    reports_extended: list[ReportExtended] = []
    for report in all_reports:
        extended_report = extend_report(report=report, current_user=current_user)
        reports_extended.append(extended_report)

    return reports_extended


def get_report_extended(report_id: str, current_user: User) -> ReportExtended:

    report: Report = get_report(report_id=report_id, current_user=current_user)

    return extend_report(report=report, current_user=current_user)


def extend_report(report: Report, current_user: User) -> ReportExtended:

    attached_assessment: Assessment = assessment_service.get_assessment(assessment_id=report.assessment_id, current_user=current_user)

    return ReportExtended(
            report_id=report.report_id,
            report_name=report.report_name,
            assessment_id=attached_assessment.assessment_id,
            assessment_name=attached_assessment.assessment_name,
            assessment_owner=attached_assessment.owner_name,
            public=report.public,
            key=report.key,
            summary=report.summary,
            recommendation_title_1=report.recommendation_title_1,
            recommendation_content_1=report.recommendation_content_1,
            recommendation_title_2=report.recommendation_title_2,
            recommendation_content_2=report.recommendation_content_2,
            recommendation_title_3=report.recommendation_title_3,
            recommendation_content_3=report.recommendation_content_3,
            )

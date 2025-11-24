import uuid
import os
import secrets


from app.data import report as data
from app.data import assessment as assessment_data

from app.service import assessment as assessment_service

from app.model.report import Report, ReportCreate, ReportExtended, ReportUpdate
from app.model.user import User
from app.model.assesment import Assessment, AssessmentQA

from app.exception.service import EndpointDataMismatch, Unauthorized

from app.template.init import jinja
from app.config import UPLOADS_DIR


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


def get_public_reports_for_assessment(assessment_id: str, current_user: User) -> list[Report]:

    reports = data.get_public_reports_for_assessment(assessment_id=assessment_id)
    assessment = assessment_data.get_one(assessment_id=assessment_id)

    if current_user.user_id != assessment.owner_id:
        raise Unauthorized(msg="This assessment doesn't belong to you. You can not view it's content")

    return reports


def get_public_report_for_user(report_id: str, current_user: User) -> Report:

    if current_user.user_id == None:
        raise Unauthorized(msg="Seems you are not authorized. Try logging in again.")

    report = data.get_public_report_for_user(report_id=report_id)
    assessment = assessment_data.get_one_for_user(assessment_id=report.assessment_id, user_id=current_user.user_id)

    if current_user.user_id != assessment.owner_id:
        raise Unauthorized(msg="Looks like the requested report doesn't belong to you.")

    return report




def update_report(report_id: str, report_update: ReportUpdate, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    if not report_id == report_update.report_id:
        raise EndpointDataMismatch(msg="Provided report object doesn't match endpoint ID.")

    return data.update_report(report_update=report_update)


def delete_report(report_id: str, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    try:
        report = data.delete_report(report_id=report_id)
        if report.wheel_filename:
            os.remove(UPLOADS_DIR / report.wheel_filename)
    except Exception as e:
        # Not sure what can go wrong here
        raise e

    return report


def create_report(report_create: ReportCreate, current_user: User) -> Report:

    if not current_user.can_manage_reports():
        raise Unauthorized(msg="You cannot manage reports.")

    wheel_filename = create_wheel_snapshot(assessment_id=report_create.assessment_id, current_user=current_user )

    report = Report(
            report_id=str(uuid.uuid4()),
            report_name=report_create.report_name,
            assessment_id=report_create.assessment_id,
            public=False,
            key=secrets.token_urlsafe(16),
            wheel_filename=wheel_filename,
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
            wheel_filename=report.wheel_filename,
            summary=report.summary,
            recommendation_title_1=report.recommendation_title_1,
            recommendation_content_1=report.recommendation_content_1,
            recommendation_title_2=report.recommendation_title_2,
            recommendation_content_2=report.recommendation_content_2,
            recommendation_title_3=report.recommendation_title_3,
            recommendation_content_3=report.recommendation_content_3,
            )

def create_wheel_snapshot(assessment_id: str, current_user: User) -> str:
    """Takes in the assessment_id and generates the svg file containing the
    report wheel snapshot and returns it's name to the calling function."""

    context = {}

    filename = str(uuid.uuid4()) + ".svg"

    # Ensure uploads directory exists
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    assessment_qa: list[AssessmentQA] = assessment_service.get_all_qa(assessment_id=assessment_id, current_user=current_user)
    context["wheel"] = assessment_service.prepare_wheel_context(assessment_qa)

    template = jinja.env.get_template("wheel/wheel-report.svg")
    content = template.render(context)

    with open(UPLOADS_DIR / filename, "w") as file:
        file.write(content)

    return filename

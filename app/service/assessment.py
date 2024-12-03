from app.model.assesment import Assessment, AssessmentNew
from app.model.user import User
from app.exception.service import Unauthorized
import app.data.assessment as data




def create_assessment(assessment_new: AssessmentNew, current_user: User) -> Assessment:

    if not current_user.can_manage_assessments():
        raise Unauthorized(msg="You cannot manage assessments.")

    created_assessment: Assessment = data.create_assessment(assessment_new=assessment_new)
    return created_assessment


def get_assessment(assessment_id: str, current_user: User) -> Assessment:

    assessment = data.get_one(assessment_id=assessment_id)
    
    if not current_user.can_manage_assessments() or assessment.owner_id != current_user.user_id:
        raise Unauthorized(msg="You cannot access this assessment.")

    return assessment


def save_answer():

    return


def get_question():

    return

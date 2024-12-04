from uuid import uuid4
from app.model.assesment import Assessment, AssessmentNew, AssessmentPost
from app.model.user import User
from app.exception.service import Unauthorized
import app.data.assessment as data




def create_assessment(assessment_post: AssessmentPost, current_user: User) -> Assessment:

    if not current_user.can_manage_assessments():
        raise Unauthorized(msg="You cannot manage assessments.")

    assessment_new: AssessmentNew = AssessmentNew(
            assessment_id=str(uuid4()),
            assessment_name=assessment_post.assessment_name,
            owner_id=assessment_post.owner_id
            ) 
    created_assessment: Assessment = data.create_assessment(assessment_new=assessment_new)
    return created_assessment


def get_assessment(assessment_id: str, current_user: User) -> Assessment:

    assessment = data.get_one(assessment_id=assessment_id)
    
    if not current_user.can_manage_assessments() or assessment.owner_id != current_user.user_id:
        raise Unauthorized(msg="You cannot access this assessment.")

    return assessment


def get_all(current_user: User) -> list[Assessment]:

    if not current_user.can_manage_assessments():
        raise Unauthorized(msg="You cannot view all assessments.")

    return data.get_all()


def save_answer():

    return


def get_question():

    return


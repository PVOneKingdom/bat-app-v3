from uuid import uuid4
from app.exception.database import RecordNotFound
from app.model.assesment import Assessment, AssessmentAnswerPost, AssessmentNew, AssessmentPost, AssessmentQA
from app.model.user import User
from app.exception.service import Unauthorized
from app.template.init import jinja

import app.data.assessment as data
from app.service import report as report_service




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
    
    if not current_user.can_manage_assessments() and assessment.owner_id != current_user.user_id:
        raise Unauthorized(msg="You cannot access this assessment.")

    return assessment


def delete_assessment(assessment_id: str, current_user: User) -> Assessment:

    assessment = data.delete_assessment(assessment_id=assessment_id)
    
    if not current_user.can_manage_assessments():
        raise Unauthorized(msg="You cannot access this assessment.")

    return assessment


def get_all(current_user: User) -> list[Assessment]:

    if not current_user.can_manage_assessments():
        raise Unauthorized(msg="You cannot view all assessments.")

    return data.get_all()


def get_all_for_user(current_user: User) -> list[Assessment]:

    if current_user.user_id == None:
        raise Unauthorized(msg="Seems that you are not authorized. Try logging in again.")

    assessments = data.get_all_for_user(user_id=current_user.user_id) 
    for assessment in assessments:
        reports = report_service.get_public_reports_for_assessment(assessment_id=assessment.assessment_id, current_user=current_user)
        if reports:
            assessment.has_reports = True

    return assessments

def get_for_user(assessment_id: str | None, current_user: User) -> Assessment:
    
    if assessment_id == None:
        raise ValueError("Value assessment_id is None, cannot fetch Assessment object")

    if current_user.user_id == None:
        raise Unauthorized("Seems that you cannot access this resource. If it's mistake let us know.")

    return data.get_one_for_user(assessment_id=assessment_id, user_id=current_user.user_id)



def get_all_qa(assessment_id: str, current_user: User) -> list[AssessmentQA]:

    assessment = data.get_one(assessment_id=assessment_id)

    if not current_user.can_manage_assessments() and current_user.user_id != assessment.owner_id:
        raise Unauthorized(msg="You cannot access this assessment data.")

    return data.filter_assessment_qa_by_category_order_and_question_id(assessment_id=assessment_id)


def prepare_wheel_context(assessment_qa: list[AssessmentQA]) -> dict:

    context: dict = {
            "assessment_id":assessment_qa[0].assessment_id
            }

    for qa in assessment_qa:
        category_name_key = f"category_name_{qa.category_order:02}"
        if category_name_key not in context:
            context[category_name_key] = qa.category_name

        category_order_key = f"category_{qa.category_order:02}_order"
        if category_order_key not in context:
            context[category_order_key] = f"{qa.category_order}"

        field_color: str = "#000000"
        match qa.answer_option:
            case "yes":
                field_color = "#00cd00"
            case "mid":
                field_color = "#cdcd00"
            case "no":
                field_color = "#cd0000"
            case _:
                field_color = "#0000cd"
        question_key = f"category_{qa.category_order:02}_question_{qa.question_order}"
        context[question_key] = field_color

    return context


def filter_assessment_qa_by_category_order_and_question_id(assessment_qa: list[AssessmentQA], category_order: int, question_order: int) -> AssessmentQA:

    for qa in assessment_qa:
        if qa.category_order == category_order and qa.question_order == question_order:
            return qa

    raise RecordNotFound(msg=f"Unable to find Assessment Q&A with cateogory order: {category_order} and question_order: {question_order}")

def filter_assessment_qa_by_category(assessment_qa: list[AssessmentQA], category_order: int) -> list[AssessmentQA]:

    filtered_qas = []

    for qa in assessment_qa:
        if qa.category_order == category_order:
            filtered_qas.append(qa)

    if filtered_qas:
        return filtered_qas
    else:
        raise RecordNotFound(msg=f"Unable to find Assessment Q&A with cateogory order: {category_order}.")


def get_neighbouring_questions(assessment_qa: list[AssessmentQA], category_order: int, question_order: int):

    orders: list = []
    for i in range(0, 13):
        for y in range(1, 5):
            orders.append((i,y))

    previous_question = None
    next_question = None

    current_index = orders.index((category_order, question_order))
    if current_index == 0:
        previous_question = None
        next_question = filter_assessment_qa_by_category_order_and_question_id(assessment_qa=assessment_qa, category_order=orders[current_index + 1][0], question_order=orders[current_index + 1][1])
    elif current_index == len(orders) - 1:
        previous_question = filter_assessment_qa_by_category_order_and_question_id(assessment_qa=assessment_qa, category_order=orders[current_index - 1][0], question_order=orders[current_index - 1][1])
        next_question = None
    else:
        previous_question = filter_assessment_qa_by_category_order_and_question_id(assessment_qa=assessment_qa, category_order=orders[current_index - 1][0], question_order=orders[current_index - 1][1])
        next_question = filter_assessment_qa_by_category_order_and_question_id(assessment_qa=assessment_qa, category_order=orders[current_index + 1][0], question_order=orders[current_index + 1][1])

    return (previous_question, next_question)

    
def save_answer(answer_data: AssessmentAnswerPost, current_user: User):

    targeted_assessment = get_assessment(assessment_id=answer_data.assessment_id, current_user=current_user)
    
    if current_user.can_manage_assessments() or current_user.user_id == targeted_assessment.owner_id:
        data.save_answer(answer_data=answer_data)

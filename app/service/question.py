from app.data import question as data
import json
from pathlib import Path

from app.exception.service import EndpointDataMismatch, Unauthorized
from app.model.question import Question, QuestionCategory, QuestionCategoryRename, QuestionCategoryReorder, QuestionEditContent
from app.model.user import User



# -------------------------------
#   Add default questions and categories
# -------------------------------

def add_default_questions():
    """Depends on the presence of the default_quesions.json file in the same direcotry."""

    path = Path(__file__).resolve().parent
    json_file_path = path / "default_questions.json"

    json_content: str = ""
    with open(json_file_path, "r") as file:
        json_content = file.read()

    category_names: list[str] = []

    questions: list[dict] = json.loads(json_content)

    data.delete_questions()
    data.delete_categories()

    for i in range(0,13):
        for key, val in questions[i].items():
            print(f"Beam: {key}")
            category_name = questions[i][key]["title"]
            print(f"Category name: {category_name},\nCategory order: {i}")
            category_row_id = data.load_category(category_name=category_name, category_order=i)
            print("\n")
            for q_id in range(1,5):
                question = questions[i][key]["segment1"][f"question{q_id}"]["title"]
                question_description = ""
                if questions[i][key]["segment1"][f"question{q_id}"]["commentTitle"] != "":
                    question_description = questions[i][key]["segment1"][f"question{q_id}"]["commentTitle"]
                if questions[i][key]["segment1"][f"question{q_id}"]["commentDescription"] != "":
                    question_description = questions[i][key]["segment1"][f"question{q_id}"]["commentDescription"]
                question_no = questions[i][key]["segment1"][f"question{q_id}"]["radio"]["option1"]
                question_mid = questions[i][key]["segment1"][f"question{q_id}"]["radio"]["option2"]
                question_yes = questions[i][key]["segment1"][f"question{q_id}"]["radio"]["option3"]
                print(f"{question}\n{question_description}\n{question_no}\n{question_yes}\n{question_mid}")
                data.load_question(
                        question=question, question_description=question_description, question_order=q_id,
                        option_no=question_no, option_yes=question_yes, option_mid=question_mid,
                        category_id=category_row_id
                        )

# -------------------------------
#   CRUD
# -------------------------------

def get_all(current_user: User) -> list[Question]:

    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")

    return data.get_all()


def get_all_categories(current_user: User) -> list[QuestionCategory]:

    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")

    return data.get_all_categories()


def get_all_questions_for_category(category_id: int, current_user: User) -> list[Question]:
    
    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")

    return data.get_all_questions_for_category(category_id=category_id)


def get_questions_category(category_id: int, current_user: User) -> QuestionCategory:

    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")

    return data.get_questions_category(category_id=category_id)


def rename_questions_category(category_id_from_path: int, category_rename: QuestionCategoryRename, current_user: User) -> QuestionCategory:

    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")
    if category_id_from_path != category_rename.category_id:
        raise EndpointDataMismatch(msg="Rename data doesn't match you endpoint. Try again. Or let us know.")

    return data.rename_questions_category(category_rename=category_rename)


def reorder_questions_category(questions_category_reorder: QuestionCategoryReorder, current_user: User) -> bool:

    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")

    for category_reorder_item in questions_category_reorder.reorder_data:
        updated = data.reorder_questions_category(category_reorder_item)
        # NotImplemented - should check if all of them returns True 

    return True


def get_one(question_id: int, current_user: User) -> Question:

    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")

    return data.get_one(question_id=question_id)



def update_question_content(question_edit_content: QuestionEditContent, current_user: User) -> Question:

    if not current_user.can_manage_questions():
        raise Unauthorized(msg="You cannot manage questions.")

    return data.update_question_content(question_edit_content=question_edit_content)

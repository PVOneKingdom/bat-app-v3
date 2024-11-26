from app.data import question as data
import json
from pathlib import Path

from app.model.question import Question, QuestionCategory
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
                question                = questions[i][key]["segment1"][f"question{q_id}"]["title"]
                question_description    = questions[i][key]["segment1"][f"question{q_id}"]["description"]
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

    return data.get_all()


def get_all_categories(current_user: User) -> list[QuestionCategory]:

    return data.get_all_categories()

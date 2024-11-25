from app.data import question as data
import json
from pathlib import Path

def add_default_questions():

    path = Path(__file__).resolve().parent
    json_file_path = path / "default_questions.json"

    json_content: str = ""
    with open(json_file_path, "r") as file:
        json_content = file.read()

    category_names: list[str] = []

    questions: list[dict] = json.loads(json_content)

    data.delete_categories()

    for i in range(0,12):
        for key, val in questions[i].items():
            category_name = questions[i][key]["title"]
            print(f"Category name: {category_name}")
            data.load_category(category_name=category_name, category_order=i)
            print("\n")




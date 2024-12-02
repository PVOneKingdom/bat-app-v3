from app.data.init import conn, curs
import app.data.question as question_data
from app.model.assesment import AssessmentNew
from app.model.question import QuestionCategory


curs.execute("""create table if not exists assessments(
    assessment_id text primary key,
    assessment_name text,
    owner_id text references user( user_id ),
    last_edit text,
    last_editor text references user( user_id ),
    )""")


curs.execute("""create table if not exists assessments_questions(
    question_id integer PRIMARY KEY,
    assessment_id text references assessments( assessment_id ),
    category_id references assessments_questions_categories( category_id ),
    question text,
    question_description text,
    question_order integer,
    option_yes text,
    option_mid text,
    option_no text)""")


curs.execute("""create table if not exists assessments_questions_categories(
    category_id integer primary key,
    assessment_id text references assessments( assessment_id ),
    category_name text,
    category_order integer
    )""")


curs.execute("""create table if not exists assessments_answers(
    answer_id text pirmary key,
    assessment_id text references assessments( assessment_id ),
    question_id integer references assessments_questions( question_id ),
    answer_option text,
    answer_description text
    )""")

# -------------------------------
#   CRUDs
# -------------------------------


def create_assessment(assessment_new: AssessmentNew) -> Assessment:

    # Create new assessment entry
    qry = """insert into assessments(assessment_id, assessment_name, onwer_id)
    values(:assessment_id, :assessment_name, :owner_id)"""

    params = {
            "assessment_id": assessment_new.assessment_id,
            "assessment_name": assessment_new.assessment_name,
            "owner_id": assessment_new.onwer_id
            }

    cursor = conn.cursor()

    try:
        cursor.execute(qry, params)
    finally:
        cursor.close()


def freeze_questions_categories(assessment_id: str) -> bool:

    questions_cateogies: list[QuestionCategory] = question_data.get_all_categories()

    for category in questions_cateogies:
        
        qry = """insert into
        assessments_questions_categories(assessment_id, category_name, category_order)
        values(:assessment_id, :category_name, :category_order)"""

        params = {
                "assessment_id": assessment_id,
                "category_name": category.category_name,
                "category_order": category.category_order
                }

        cursor = conn.cursor()
        try:
            cursor.execute(qry, params)
        finally:
            cursor.close()
    
    return True


def freeze_questions(assessment_id: str) -> bool:


    return True



from app.data.init import conn, curs
import app.data.question as question_data
from app.exception.database import RecordNotFound
from app.model.assesment import Assessment, AssessmentNew
from app.model.question import Question, QuestionCategory


curs.execute("""create table if not exists assessments(
    assessment_id text primary key,
    assessment_name text,
    owner_id text references users( user_id ),
    last_edit text,
    last_editor text references users( user_id )
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

def assessment_row_to_model(row: tuple) -> Assessment:

    assessment_id, assessment_name, owner_id, \
            owner_name, last_editor, last_editor_name = row

    return Assessment(
            assessment_id=assessment_id,
            assessment_name=assessment_name,
            owner_id=owner_id,
            owner_name=owner_name,
            last_editor=last_editor,
            last_editor_name=last_editor_name
            )

# -------------------------------
#   CRUDs
# -------------------------------


def create_assessment(assessment_new: AssessmentNew) -> Assessment:

    # Create new assessment entry
    qry = """insert into assessments(assessment_id, assessment_name, owner_id)
    values(:assessment_id, :assessment_name, :owner_id)"""

    params = {
            "assessment_id": assessment_new.assessment_id,
            "assessment_name": assessment_new.assessment_name,
            "owner_id": assessment_new.owner_id
            }

    cursor = conn.cursor()

    try:
        cursor.execute(qry, params)
        conn.commit()
        return get_one(assessment_id=params["assessment_id"])
    finally:
        cursor.close()


def freeze_questions_categories(assessment_id: str) -> dict:

    questions_cateogies: list[QuestionCategory] = question_data.get_all_categories()
    category_id_map: dict = {}

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
            category_id_map[category.category_name] = cursor.lastrowid
            conn.commit()
        finally:
            cursor.close()
    
    return category_id_map


def freeze_questions(assessment_id: str, category_id_map: dict) -> bool:

    questions: list[Question] = question_data.get_all()

    for question in questions:
        qry = """insert into
        assessments_questions(assessment_id, category_id, question, question_description,
                              question_order, option_yes, option_mid, option_no)
        values(:assessment_id, :category_id, :question, :question_description,
               :question_order, :option_yes, :option_mid, :option_no)
        """

        category_id = category_id_map[question.category_name]

        params = {
                "assessment_id": assessment_id,
                "category_id": category_id,
                "question": question.question,
                "question_description,": question.question_description,
                "question_order": question.question_order,
                "option_yes": question.option_yes,
                "option_mid": question.option_mid,
                "option_no": question.option_no
                }

        cursor = conn.cursor()
        try:
            cursor.execute(qry, params)
            conn.commit()
        finally:
            cursor.close()

    return True


def get_one(assessment_id: str) -> Assessment:
    
    qry = """
    SELECT
        a.assessment_id,
        a.assessment_name,
        a.owner_id,
        u1.username as owner_name,
        a.last_editor,
        u2.username as last_editor_name,
        a.last_edit
    FROM
        assessments a
    LEFT JOIN
        users u1 ON a.owner_id = u1.user_id
    LEFT JOIN
        users u2 ON a.last_editor = u2.user_id
    WHERE 
        a.assessment_id = :assessment_id
    """

    params = {"assessment_id": assessment_id }

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        row = cursor.fetchone()
        if row:
            return assessment_row_to_model(row)
        else:
            raise RecordNotFound(msg="Requested assessment was not found.")
    finally:
        cursor.close()


def get_all() -> list[Assessment]:

    qry = """
    SELECT
        a.assessment_id,
        a.assessment_name,
        a.owner_id,
        u1.username as owner_name,
        a.last_editor,
        u2.username as last_editor_name,
        a.last_edit
    FROM
        assessments a
    LEFT JOIN
        users u1 ON a.owner_id = u1.user_id
    LEFT JOIN
        users u2 ON a.last_editor = u2.user_id
    """

    cursor = conn.cursor()
    try:
        cursor.execute(qry)
        rows = cursor.fetchall()
        if rows:
            return [assessment_row_to_model(row) for row in rows]
        else:
            return []
    finally:
        cursor.close()

from sqlite3 import Cursor, IntegrityError
from app.data.init import conn, curs
from app.model.question import Question, QuestionCategory
from app.model.user import User
from app.exception.database import RecordNotFound, UsernameOrEmailNotUnique

curs.execute("""create table if not exists questions_categories(
    category_id integer primary key,
    category_name text,
    category_order integer
    )""")

curs.execute("""create table if not exists questions(
    question_id integer PRIMARY KEY,
    category_id integer references questions_categories,
    question text,
    question_description text,
    question_order integer,
    option_yes text,
    option_mid text,
    option_no text
    )""")

# -------------------------------
#   CRUDs
# -------------------------------

def row_to_model_question(row: tuple) -> Question:

    question_id, question, question_description, question_order, \
    option_yes, option_mid, option_no, category_id, category_name, \
    category_order = row

    return Question(
            question_id=question_id,
            question=question,
            question_description=question_description,
            question_order=question_order,
            option_yes=option_yes,
            option_mid=option_mid,
            option_no=option_no,
            category_id=category_id,
            category_name=category_name,
            category_order=category_order
            )

def row_to_model_question_category(row: tuple) -> QuestionCategory:

    category_id, category_name, category_order = row

    return QuestionCategory(
            category_id=category_id,
            category_name=category_name,
            category_order=category_order,
            )

def get_all() -> list[Question]:

    qry = """select question_id, question, question_description, question_order,
    option_yes, option_mid, option_no, category_id, category_name,
    category_order from questions natural join questions_categories"""

    cursor = conn.cursor()
    try:
        cursor.execute(qry)
        rows = cursor.fetchall()
        if rows:
            return [row_to_model_question(row) for row in rows]
        else:
            raise RecordNotFound(msg="Questions were found.")
    finally:
        cursor.close()


def get_all_categories() -> list[QuestionCategory]:

    qry = """select category_id, category_name,
    category_order from questions_categories"""

    cursor = conn.cursor()
    try:
        cursor.execute(qry)
        rows = cursor.fetchall()
        if rows:
            return [row_to_model_question_category(row) for row in rows]
        else:
            raise RecordNotFound(msg="No categories were found")
    finally:
        cursor.close()


# -------------------------------
#   Default actions
# -------------------------------

def delete_categories() -> bool:
    conn.execute("delete from questions_categories")
    conn.commit()
    return True

def delete_questions() -> bool:
    conn.execute("delete from questions")
    conn.commit()
    return True

def load_category(category_name: str, category_order: int) -> int | None:

    qry = """insert into questions_categories(category_name, category_order)
    values(:category_name, :category_order)"""
    
    print(f"Loading:\ncategory_name: {category_name}\ncategory_order: {category_order}")

    params = {"category_name": category_name, "category_order": category_order}

    temp_cursor = conn.cursor()
    try:
        temp_cursor.execute(qry, params)
        conn.commit()
        return temp_cursor.lastrowid
    finally:
        temp_cursor.close()


    return temp_cursor.lastrowid

def load_question(question:str, question_description: str, question_order: int, \
        option_yes:str, option_mid:str, option_no:str, category_id: int | None) -> int | None:

    qry = """insert into questions(question, question_description, question_order, option_yes, option_mid, option_no, category_id)
    values(:question, :question_description, :question_order, :option_yes, :option_mid, :option_no, :category_id)"""

    params = {
            "question":question,
            "question_description":question_description,
            "question_order": question_order,
            "option_yes":option_yes,
            "option_mid":option_mid,
            "option_no":option_no,
            "category_id":category_id,
            }

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()

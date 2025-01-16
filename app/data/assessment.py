from uuid import uuid4
from app.data.init import conn, curs
import app.data.question as question_data
from app.exception.database import RecordNotFound
from app.model.assesment import Assessment, AssessmentAnswerPost, AssessmentNew, AssessmentQA
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
#   Central Functions
# -------------------------------

def assessment_row_to_model(row: tuple) -> Assessment:

    assessment_id, assessment_name, owner_id, \
            owner_name, last_editor, \
            last_editor_name, last_edit = row

    return Assessment(
            assessment_id=assessment_id,
            assessment_name=assessment_name,
            owner_id=owner_id,
            owner_name=owner_name,
            last_editor=last_editor,
            last_editor_name=last_editor_name,
            last_edit=last_edit,
            has_reports=None
            )


def assessment_question_row_to_model(row: tuple) -> AssessmentQA:

    question_id, \
    question, \
    question_description, \
    question_order, \
    option_yes, \
    option_mid, \
    option_no, \
    assessment_id, \
    assessment_name, \
    owner_id, \
    last_edit, \
    last_editor, \
    category_id, \
    category_name, \
    category_order, \
    answer_id, \
    answer_option, \
    answer_description = row

    return AssessmentQA(
            question_id=question_id,
            question=question,
            question_description=question_description,
            question_order=question_order,
            option_yes=option_yes,
            option_mid=option_mid,
            option_no=option_no,
            assessment_id=assessment_id,
            assessment_name=assessment_name,
            owner_id=owner_id,
            last_edit=last_edit,
            last_editor=last_editor,
            category_id=category_id,
            category_name=category_name,
            category_order=category_order,
            answer_id=answer_id,
            answer_option=answer_option,
            answer_description=answer_description
            )

# -------------------------------
#   assessment preparation
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
        category_id_map: dict = freeze_questions_categories(assessment_new.assessment_id)
        freeze_questions(assessment_id=assessment_new.assessment_id, category_id_map=category_id_map)
        prepare_answers(assessment_id=assessment_new.assessment_id)
        prepare_notes(assessment_id=assessment_new.assessment_id)
        return get_one(assessment_id=assessment_new.assessment_id)
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
                "question_description": question.question_description,
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


def prepare_answers(assessment_id: str) -> bool:

    questions: list[AssessmentQA] = filter_assessment_qa_by_category_order_and_question_id(assessment_id=assessment_id)

    qry = """insert into assessments_answers(answer_id, assessment_id, question_id)
    values(:answer_id, :assessment_id, :question_id)"""

    cursor = conn.cursor()
    try:
        for question in questions:
            params = {
                    "answer_id": str(uuid4()),
                    "assessment_id": assessment_id,
                    "question_id": question.question_id
                    }
            cursor.execute(qry, params);
        conn.commit()
        return True
    finally:
        cursor.close()


def prepare_notes(assessment_id: str) -> bool:

    qry = """insert into assessments_notes(assessment_id, category_order)
    values(:assessment_id, :category_order)"""

    cursor = conn.cursor()
    try:
        for i in range(0, 13):
            cursor.execute(qry, {"assessment_id":assessment_id, "category_order":i})
        conn.commit()
        return True
    finally:
        cursor.close()



# -------------------------------
#   CRUDs
# -------------------------------

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


def get_all_for_user(user_id: str) -> list[Assessment]:

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
        owner_id = :user_id
    """

    cursor = conn.cursor()
    try:
        cursor.execute(qry, {"user_id":user_id})
        rows = cursor.fetchall()
        if rows:
            return [assessment_row_to_model(row) for row in rows]
        else:
            return []
    finally:
        cursor.close()
    qry = """
    seelct
    """


def get_one_for_user(assessment_id: str, user_id: str) -> Assessment:

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
        a.assessment_id = :assessment_id and
        a.owner_id = :user_id
    """

    params = {
            "assessment_id": assessment_id,
            "user_id":user_id
              }

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


def delete_assessment(assessment_id: str) -> Assessment:

    assessment = get_one(assessment_id=assessment_id)

    qry_qa = """delete from assessments_answers where assessment_id = :assessment_id"""
    params_qa = {"assessment_id": assessment_id}

    qry_an = """delete from assessments_notes where assessment_id = :assessment_id"""
    params_an = {"assessment_id": assessment_id}

    qry_q = """delete from assessments_questions where assessment_id = :assessment_id"""
    params_q = {"assessment_id": assessment_id}

    qry_qc = """delete from assessments_questions_categories where assessment_id = :assessment_id"""
    params_qc = {"assessment_id": assessment_id}

    qry = """delete from assessments where assessment_id = :assessment_id"""
    params = {"assessment_id": assessment_id}


    cursor = conn.cursor()
    try:
        cursor.execute(qry_qa, params_qa)
        cursor.execute(qry_an, params_an)
        cursor.execute(qry_q, params_q)
        cursor.execute(qry_qc, params_qc)
        cursor.execute(qry_qc, params_qc)
        cursor.execute(qry, params)
        conn.commit()
        return assessment
    finally:
        cursor.close()

def filter_assessment_qa_by_category_order_and_question_id(assessment_id: str) -> list[AssessmentQA]:

    qry = """select
        q.question_id,
        q.question,
        q.question_description,
        q.question_order,
        q.option_yes,
        q.option_mid,
        q.option_no,
        q.assessment_id,
        a.assessment_name,
        a.owner_id,
        a.last_edit,
        a.last_editor,
        qc.category_id,
        qc.category_name,
        qc.category_order,
        aw.answer_id,
        aw.answer_option,
        aw.answer_description
    from 
        assessments_questions as q
    left join 
        assessments as a
        on q.assessment_id = a.assessment_id
    left join
        assessments_questions_categories as qc
        on q.category_id = qc.category_id
    left join 
        assessments_answers as aw
        on q.question_id = aw.question_id
        and q.assessment_id = aw.assessment_id
    where
        q.assessment_id = :assessment_id
    order by
        qc.category_order asc,
        q.question_order asc"""

    params = {"assessment_id":assessment_id}

    cursor = conn.cursor()
    try:
        _ = cursor.execute(qry, params)
        rows = _.fetchall()
        if rows:
            return [assessment_question_row_to_model(question) for question in rows]
        else:
            raise RecordNotFound(msg=f"Question for assessment: {assessment_id} was not found.")
    finally:
        cursor.close()
            

def save_answer(answer_data: AssessmentAnswerPost):

    qry = """
    update assessments_answers set 
        answer_option = :answer_option,
        answer_description = :answer_description
    where
        answer_id = :answer_id
    """
    
    params = {
            "answer_option":answer_data.answer_option,
            "answer_description":answer_data.answer_description,
            "answer_id":answer_data.answer_id
            }

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
    finally:
        cursor.close()

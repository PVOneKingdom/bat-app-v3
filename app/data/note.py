import json

from app.data.init import conn
from app.exception.database import RecordNotFound
from app.model.assesment import AssessmentNote, AssessmentNoteExtended



# -------------------------------
#   Table creation
# -------------------------------


conn.execute("""
             create table if not exists assessments_notes(
                 note_id integer primary key,
                 assessment_id text references assessments( assessment_id ),
                 category_order int,
                 note_content text
                 )
             """)


# -------------------------------
#   Central Functions
# -------------------------------

def row_to_note_model(row: tuple) -> AssessmentNote:

    note_id, \
    assessment_id, \
    category_order, \
    note_content = row

    if note_content:
        note_content = json.loads(note_content)
    else:
        note_content = None


    return AssessmentNote(
            note_id=note_id,
            assessment_id=assessment_id,
            category_order=category_order,
            note_content=note_content
            )

def row_to_extended_note_model(row: tuple) -> AssessmentNoteExtended:

    note_id, \
    assessment_id, \
    category_order, \
    note_content, \
    category_name = row

    if note_content:
        note_content = json.loads(note_content)
    else:
        note_content = None

    return AssessmentNoteExtended(
            note_id=note_id,
            assessment_id=assessment_id,
            category_order=category_order,
            note_content=note_content,
            category_name=category_name
            )


# -------------------------------
#   CRUDs
# -------------------------------


def create_notes(assessment_id: str, category_order: int) -> bool:

    qry = """
    insert into
        assessments_notes(assessment_id, category_order)
        values(:assessment_id, :category_order)
    """

    cursor = conn.cursor()

    try:
        cursor.execute(qry, {"assessment_id": assessment_id, "category_order": category_order})
        conn.commit()
        return True
    finally:
        cursor.close()


def get_assessment_notes(assessment_id: str) -> list[AssessmentNoteExtended]:

    qry = """
    select
        note_id,
        assessment_id,
        category_order,
        note_content,
        category_name
    from
        assessments_notes
    natural join
        assessments_questions_categories
    where
        assessment_id = :assessment_id
    """

    params = {
            "assessment_id": assessment_id,
            }

    cursor = conn.cursor()

    try:
        cursor.execute(qry, params)
        rows = cursor.fetchall()
        if rows:
            return [row_to_extended_note_model(row) for row in rows]
        else:
            raise RecordNotFound(msg="No note found.")
    finally:
        cursor.close()


def get_note(assessment_id: str, category_order: int) -> AssessmentNote:
    
    qry = """
    select
        note_id,
        assessment_id,
        category_order,
        note_content
    from
        assessments_notes
    where
        assessment_id = :assessment_id and
        category_order = :category_order
    """

    params = {
            "assessment_id": assessment_id,
            "category_order": category_order
            }

    cursor = conn.cursor()

    try:
        cursor.execute(qry, params)
        row = cursor.fetchone()
        if row:
            return row_to_note_model(row)
        else:
            raise RecordNotFound(msg="No note found.")
    finally:
        cursor.close()


def get_note_by_id(note_id: int) -> AssessmentNote:
    
    qry = """
    select
        note_id,
        assessment_id,
        category_order,
        note_content
    from
        assessments_notes
    where
        note_id = :note_id
    """

    params = {
            "note_id": note_id
            }

    cursor = conn.cursor()

    try:
        cursor.execute(qry, params)
        row = cursor.fetchone()
        if row:
            return row_to_note_model(row)
        else:
            raise RecordNotFound(msg="No note found.")
    finally:
        cursor.close()


def update_note(note_id: int, note_content: dict) -> AssessmentNote:

    qry = """
    update
        assessments_notes
    set
        note_content = :note_content
    where
        note_id = :note_id
    """

    note_to_save = None
    if note_content:
        note_to_save = json.dumps(note_content)

    params = {
            "note_id":note_id,
            "note_content":note_to_save
            }

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        return get_note_by_id(note_id=note_id)
    finally:
        cursor.close()


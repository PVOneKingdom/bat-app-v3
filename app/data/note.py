from app.data.init import conn
from app.exception.database import RecordNotFound
from app.model.note import Note
from app.model.report import Report


# -------------------------------
#   Table creation
# -------------------------------


conn.execute("""
             create table if not exists notes(
                 note_id integer primary key,
                 assessment_id text references assessments( assessment_id ),
                 category_order int,
                 note_content text
                 )
             """)


# -------------------------------
#   Central Functions
# -------------------------------

def row_to_note_model(row: tuple) -> Note:

    note_id, \
    assessment_id, \
    category_order, \
    note_content = row

    return Note(
            note_id=note_id,
            assessment_id=assessment_id,
            category_order=category_order,
            note_content=note_content
            )



# -------------------------------
#   CRUDs
# -------------------------------


def create_notes(assessment_id: str, category_order: int) -> bool:

    qry = """
    insert into
        notes(assessment_id, category_order)
        values(:assessment_id, :category_order)
    """

    cursor = conn.cursor()

    try:
        cursor.execute(qry, {"assessment_id": assessment_id, "category_order": category_order})
        conn.commit()
        return True
    finally:
        cursor.close()



def get_note(assessment_id: str, category_order: int) -> Note:
    
    qry = """
    select
        note_id,
        assessment_id,
        category_order,
        note_content
    form
        notes
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
        return row_to_note_model(row)
    finally:
        conn.close()
        


def get_note_by_id(note_id: int) -> Note:
    
    qry = """
    select
        note_id,
        assessment_id,
        category_order,
        note_content
    form
        notes
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
        return row_to_note_model(row)
    finally:
        conn.close()

def update_note(note_id: int, note_content: str) -> Note:

    qry = """
    update
        note
    set
        note_content = :note_content
    where
        note_id = :note_id
    """

    params = {
            "note_id":note_id,
            "note_content":note_content
            }

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        conn.commit()
        return get_note_by_id(note_id=note_id)
    finally:
        cursor.close()


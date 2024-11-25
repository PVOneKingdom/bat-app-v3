from sqlite3 import IntegrityError
from app.data.init import conn, curs
from app.model.user import User
from app.exception.database import RecordNotFound, UsernameOrEmailNotUnique

curs.execute("""create table if not exists questions_categories(
    category_id integer primary key,
    category_name text,
    category_order integer
    )""")

curs.execute("""create table if not exists questions(
    questoin_id text PRIMARY KEY,
    category_id integer references questions_categories,
    question text,
    question_description text,
    option_yes text,
    option_mid text,
    option_no text
    )""")

def delete_categories() -> bool:
    conn.execute("delete from questions_categories")
    conn.commit()
    return True

def load_category(category_name: str, category_order: int) -> bool:

    qry = """insert into questions_categories(category_name, category_order)
    values(:category_name, :category_order)"""

    params = {"category_name": category_name, "category_order": category_order}
    _ = conn.execute(qry, params)
    conn.commit()
    return True


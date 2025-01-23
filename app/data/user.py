from sqlite3 import IntegrityError
from app.data.init import conn, curs
from app.model.user import User
from app.exception.database import RecordNotFound, UsernameOrEmailNotUnique


curs.execute("""create table if not exists users(
    user_id text PRIMARY KEY,
    username text unique,
    email text unique,
    hash text,
    role text
    )""")

def row_to_model(row: tuple) -> User:
    user_id, username, email, hash, role = row
    return User(
        user_id=user_id,
        username=username,
        email=email,
        hash=hash,
        role=role
    )


def model_to_dict(user: User) -> dict:
    return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "hash": user.hash,
            "role": user.role.value,
            }


def get_one(user_id: str | None) -> User:

    qry = "select * from users where user_id = :user_id"
    params = {"user_id": user_id}

    cursor = conn.cursor()
    try:
        cursor.execute(qry, params)
        row = cursor.fetchone()
        if row:
            return row_to_model(row)
        else:
            raise RecordNotFound(msg="User was not found")
    finally:
        cursor.close()


def get_all() -> list[User]:
    qry = "select * from users"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]


def get_by(field: str, value: str|int ) -> User:
    qry = f"select * from users where {field} = :value"
    params = {
            "value": value,
        }
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise RecordNotFound(f"Record for {field}: {value} was not found")


def create(user: User) -> User:
    qry = """insert into users(user_id, username, email, hash, role) 
            values( :user_id, :username, :email, :hash, :role)"""
    try:
        params = model_to_dict(user)
        params["email"] = params["email"].lower()
        _ = curs.execute(qry, params)
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        if "UNIQUE constraint failed: user.email" in str(e):
            raise UsernameOrEmailNotUnique(msg="Email needs to be unique. Provided e-mail is already in use. Try different one.")
        if "UNIQUE constraint failed: user.username" in str(e):
            raise UsernameOrEmailNotUnique(msg="Username needs to be unique. Provided username is used. Try different one.")
    return get_one(user.user_id)


def modify(user_id: str, user_updated: User) -> User:

    qry = """update users set
        username=:username,
        email=:email,
        hash=:hash,
        role=:role
        where user_id = :user_id"""
    params = model_to_dict(user_updated)
    params["email"] = params["email"].lower()
    params["user_id"] = user_id
    try:
        _ = curs.execute(qry, params)
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        if "UNIQUE constraint failed: user.email" in str(e):
            raise UsernameOrEmailNotUnique(msg="Email needs to be unique. Provided e-mail is already in use. Try different one.")
        if "UNIQUE constraint failed: user.username" in str(e):
            raise UsernameOrEmailNotUnique(msg="Username needs to be unique. Provided username is used. Try different one.")
    updated_user = get_one(user_id)
    return updated_user


def delete(user_id: str) -> User:
    deleted_user = get_one(user_id)

    qry = "delete from users where user_id = :user_id"
    params = {
            "user_id": user_id
        }
    conn.execute(qry, params)
    conn.commit()
    return deleted_user

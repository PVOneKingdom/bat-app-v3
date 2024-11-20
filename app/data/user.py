from sqlite3 import IntegrityError
from app.data.init import conn, curs
from app.model.user import User
from app.exception.database import RecordNotFound, UsernameOrEmailNotUnique


curs.execute("""create table if not exists user(
    id text PRIMARY KEY,
    username text unique,
    email text unique,
    hash text,
    role text
    )""")

def row_to_model(row: tuple) -> User:
    id, username, email, hash, role = row
    return User(
        id=id,
        username=username,
        email=email,
        hash=hash,
        role=role
    )


def model_to_dict(user: User) -> dict:
    return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "hash": user.hash,
            "role": user.role.value,
            }


def get_one(id: str | None) -> User:
    qry = "select * from user where id = :id"
    params = {"id": id}
    curs.execute(qry, params)
    row = curs.fetchone()
    if row:
        return row_to_model(row)
    else:
        raise RecordNotFound(msg="User was not found")


def get_all() -> list[User]:
    qry = "select * from user"
    curs.execute(qry)
    return [row_to_model(row) for row in curs.fetchall()]


def get_by(field: str, value: str|int ) -> User:
    qry = f"select * from user where {field} = :value"
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
    qry = """insert into user(id, username, email, hash, role) 
            values( :id, :username, :email, :hash, :role)"""
    try:
        _ = curs.execute(qry, model_to_dict(user))
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        if "UNIQUE constraint failed: user.email" in str(e):
            raise UsernameOrEmailNotUnique(msg="Email needs to be unique. Provided e-mail is already in use. Try different one.")
        if "UNIQUE constraint failed: user.username" in str(e):
            raise UsernameOrEmailNotUnique(msg="Username needs to be unique. Provided username is used. Try different one.")
    return get_one(user.id)


def modify(id: str, user_updated: User) -> User:

    qry = """update user set
        username=:username,
        email=:email,
        hash=:hash,
        role=:role
        where uuid = :uuid"""
    params = model_to_dict(user_updated)
    params["id"] = id
    try:
        _ = curs.execute(qry, params)
        conn.commit()
    except IntegrityError as e:
        conn.rollback()
        if "UNIQUE constraint failed: user.email" in str(e):
            raise UsernameOrEmailNotUnique(msg="Email needs to be unique. Provided e-mail is already in use. Try different one.")
        if "UNIQUE constraint failed: user.username" in str(e):
            raise UsernameOrEmailNotUnique(msg="Username needs to be unique. Provided username is used. Try different one.")
    updated_user = get_one(id)
    return updated_user


def delete(id: str) -> User:
    deleted_user = get_one(id)
    qry = "delete from user where id= :id"
    params = {
            "id": id
        }
    conn.execute(qry, params)
    conn.commit()
    return deleted_user

from app.exception.service import Unauthorized
from app.model.note import Note
from app.model.user import User

import app.data.note as data


def get_note(assessment_id: str, category_order: int, current_user: User) -> Note

    if not current_user.can_manage_notes():
        raise Unauthorized(msg="You cannot manage notes.")

    return data.get_note(assessment_id=assessment_id, category_order=category_order)


def get_note_by_id(note_id: int, current_user: User) -> Note:

    if not current_user.can_manage_notes():
        raise Unauthorized(msg="You cannot manage notes.")

    return data.get_note_by_id(note_id=note_id)


def update_note(note_id: int, note_content: str, current_user: User) -> Note:

    if not current_user.can_manage_notes():
        raise Unauthorized(msg="You cannot manage notes.")

    return data.update_note(note_id=note_id, note_content=note_content)

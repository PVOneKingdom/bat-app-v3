from pydantic import BaseModel

class Note(BaseModel):
    note_id: int | None
    assessment_id: str
    category_order: int
    note_content: str | None

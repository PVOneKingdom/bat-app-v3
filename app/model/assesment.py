from pydantic import BaseModel

class Assessment(BaseModel):
    assessment_id: str
    assessment_name: str
    owner_id: str | None
    owner_name: str | None
    last_editor: str | None
    last_editor_name: str | None
    last_edit: str | None


class AssessmentPost(BaseModel):
    assessment_name: str
    owner_id: str

class AssessmentNew(BaseModel):
    assessment_id: str
    assessment_name: str
    owner_id: str


class AssessmentQuestion(BaseModel):
    question_id: int
    assessment_id: str
    assessment_name: str
    owner_id: str
    last_edit: str | None
    last_editor: str | None
    category_id: int
    category_name: str
    category_order: int


class AssessmentQuestionCategory(BaseModel):
    category_id: int
    assessment_id: str
    category_name: str
    category_order: int

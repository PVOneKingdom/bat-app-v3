from pydantic import BaseModel

class Assessment(BaseModel):
    assessment_id: str
    assessment_name: str
    owner_id: str | None
    owner_name: str | None
    last_editor: str | None
    last_editor_name: str | None


class AssessmentNew(BaseModel):
    assessment_id: str | None
    assessment_name: str
    owner_id: str


class AssessmentQuestion(BaseModel):
    assessment_id: str
    assessment_name: str
    onwer_id: str
    last_edit: str
    last_editor: str
    question_id: int
    category_id: int
    category_name: str


class AssessmentQuestionCategory(BaseModel):
    category_id: int
    assessment_id: str
    category_name: str
    category_order: int

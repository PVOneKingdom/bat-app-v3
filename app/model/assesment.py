from pydantic import BaseModel


class Assessment(BaseModel):
    assessment_id: str
    assessment_name: str
    owner_id: str | None
    owner_name: str | None
    last_editor: str | None
    last_editor_name: str | None
    last_edit: str | None
    has_reports: bool | None


class AssessmentPost(BaseModel):
    assessment_name: str
    owner_id: str


class AssessmentAnswerPost(BaseModel):
    answer_id: str
    assessment_id: str
    question_order: int
    answer_option: str
    answer_description: str


class AssessmentNew(BaseModel):
    assessment_id: str
    assessment_name: str
    owner_id: str


class AssessmentQA(BaseModel):
    question_id: int
    question: str
    question_description: str
    question_order: int
    option_yes: str
    option_mid: str
    option_no: str
    assessment_id: str
    assessment_name: str
    owner_id: str
    last_edit: str | None
    last_editor: str | None
    category_id: int
    category_name: str
    category_order: int
    answer_id: str | None
    answer_option: str | None
    answer_description: str | None


class AssessmentQuestionCategory(BaseModel):
    category_id: int
    assessment_id: str
    category_name: str
    category_order: int


class AssessmentNote(BaseModel):
    note_id: int | None
    assessment_id: str
    category_order: int
    note_content: str | None


class AssessmentNoteExtended(BaseModel):
    note_id: int | None
    assessment_id: str
    category_order: int
    note_content: str | None
    category_name: str | None

from pydantic import BaseModel


class Question(BaseModel):
    question_id: int
    question: str
    question_description: str
    question_order: int
    option_yes: str
    option_mid: str
    option_no: str
    category_id: int
    category_name: str
    category_order: int

class QuestionCategory(BaseModel):
    category_id: int
    category_name: str
    category_order: int

from pydantic import BaseModel

class Report(BaseModel):
    report_id: str
    assessment_id: str
    public: bool
    key: str
    report_time: str | None
    summary: str | None
    recommendation_title_1: str | None
    recommendation_content_1: str | None
    recommendation_title_2: str | None
    recommendation_content_2: str | None
    recommendation_title_3: str | None
    recommendation_content_3: str | None


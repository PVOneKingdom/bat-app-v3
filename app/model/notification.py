from pydantic import BaseModel


class Notification(BaseModel):
    style: str
    content: str

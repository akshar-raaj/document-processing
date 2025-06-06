from pydantic import BaseModel


class ConverseModel(BaseModel):
    text: str
    question: str
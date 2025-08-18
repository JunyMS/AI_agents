from typing import Annotated
from pydantic import BaseModel
from pydantic.types import conlist

class ClarificationQuestions(BaseModel):
    questions: Annotated[list[str], conlist(str, min_length=3, max_length=3)]

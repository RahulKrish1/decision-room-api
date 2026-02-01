from pydantic import BaseModel, Field
from typing import List

class PollCreateRequest(BaseModel):
    question: str = Field(min_length=1, max_length=300)
    options: List[str] = Field(min_length=2, max_length=20)

class PollOptionResponse(BaseModel):
    id: int
    text: str
    position: int

class PollResponse(BaseModel):
    id: int
    room_id: int
    question: str
    status: str
    options: List[PollOptionResponse]

class VoteRequest(BaseModel):
    option_id: int

class PollResultRow(BaseModel):
    option_id: int
    votes: int

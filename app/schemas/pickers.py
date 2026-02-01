from pydantic import BaseModel, Field
from typing import List

class PickerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class PickerOptionCreateRequest(BaseModel):
    label: str = Field(min_length=1, max_length=120)

class PickerOptionResponse(BaseModel):
    id: int
    label: str
    active: bool

class PickerResponse(BaseModel):
    id: int
    room_id: int
    name: str
    options: List[PickerOptionResponse]

class PickResponse(BaseModel):
    event_id: int
    picked_option_id: int | None
    commit_hash: str
    reveal_seed: str  # for MVP you can reveal immediately; later you can delay reveal

class PickEventResponse(BaseModel):
    id: int
    picked_option_id: int | None
    commit_hash: str
    reveal_seed: str

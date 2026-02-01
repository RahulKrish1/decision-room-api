from pydantic import BaseModel, Field

class RoomCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class RoomResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    owner_id: int

class JoinRoomRequest(BaseModel):
    invite_code: str = Field(min_length=6, max_length=32)

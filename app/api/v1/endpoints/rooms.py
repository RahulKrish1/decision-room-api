from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.dependencies_auth import get_current_user
from app.crud.rooms import create_room, list_rooms_for_user, get_room_for_member, join_room_by_code
from app.schemas.rooms import RoomCreateRequest, RoomResponse, JoinRoomRequest

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("", response_model=RoomResponse, status_code=201)
def create(payload: RoomCreateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room = create_room(db, owner_id=current_user.id, name=payload.name)
    return RoomResponse(id=room.id, name=room.name, invite_code=room.invite_code, owner_id=room.owner_id)

@router.get("", response_model=list[RoomResponse])
def list_my_rooms(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rooms = list_rooms_for_user(db, user_id=current_user.id)
    return [RoomResponse(id=r.id, name=r.name, invite_code=r.invite_code, owner_id=r.owner_id) for r in rooms]

@router.get("/{room_id}", response_model=RoomResponse)
def get(room_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room = get_room_for_member(db, room_id=room_id, user_id=current_user.id)
    if not room:
        raise HTTPException(status_code=404, detail="room_not_found")
    return RoomResponse(id=room.id, name=room.name, invite_code=room.invite_code, owner_id=room.owner_id)

@router.post("/join", response_model=RoomResponse)
def join(payload: JoinRoomRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    room = join_room_by_code(db, invite_code=payload.invite_code, user_id=current_user.id)
    if not room:
        raise HTTPException(status_code=404, detail="invalid_invite_code")
    return RoomResponse(id=room.id, name=room.name, invite_code=room.invite_code, owner_id=room.owner_id)

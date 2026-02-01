from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.dependencies_auth import get_current_user
from app.models.room_member import RoomMember

def require_room_member(room_id: int, db: Session, user_id: int) -> None:
    exists = db.scalar(
        select(RoomMember).where(RoomMember.room_id == room_id, RoomMember.user_id == user_id)
    )
    if not exists:
        raise HTTPException(status_code=403, detail="not_a_room_member")

def room_member_dep(room_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    require_room_member(room_id, db, current_user.id)
    return current_user

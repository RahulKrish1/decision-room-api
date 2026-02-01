from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.room import Room
from app.models.room_member import RoomMember
from app.services.invite_codes import new_invite_code

def create_room(db: Session, *, owner_id: int, name: str) -> Room:
    # try a few times in case invite_code collides (very unlikely)
    for _ in range(5):
        room = Room(owner_id=owner_id, name=name, invite_code=new_invite_code())
        db.add(room)
        db.flush()  # get room.id without committing

        db.add(RoomMember(room_id=room.id, user_id=owner_id, role="owner"))
        try:
            db.commit()
            db.refresh(room)
            return room
        except IntegrityError:
            db.rollback()
    raise RuntimeError("failed_to_generate_invite_code")

def list_rooms_for_user(db: Session, *, user_id: int) -> list[Room]:
    stmt = (
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(RoomMember.user_id == user_id)
        .order_by(Room.created_at.desc())
    )
    return list(db.scalars(stmt).all())

def get_room_for_member(db: Session, *, room_id: int, user_id: int) -> Room | None:
    stmt = (
        select(Room)
        .join(RoomMember, RoomMember.room_id == Room.id)
        .where(Room.id == room_id, RoomMember.user_id == user_id)
    )
    return db.scalar(stmt)

def join_room_by_code(db: Session, *, invite_code: str, user_id: int) -> Room | None:
    room = db.scalar(select(Room).where(Room.invite_code == invite_code))
    if not room:
        return None

    # insert membership if not exists
    existing = db.get(RoomMember, {"room_id": room.id, "user_id": user_id})
    if existing:
        return room

    db.add(RoomMember(room_id=room.id, user_id=user_id, role="member"))
    db.commit()
    return room

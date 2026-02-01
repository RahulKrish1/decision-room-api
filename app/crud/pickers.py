from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.picker import Picker
from app.models.picker_option import PickerOption
from app.models.pick_event import PickEvent

def create_picker(db: Session, *, room_id: int, user_id: int, name: str) -> Picker:
    picker = Picker(room_id=room_id, created_by=user_id, name=name)
    db.add(picker)
    db.commit()
    db.refresh(picker)
    return picker

def add_option(db: Session, *, picker_id: int, label: str) -> PickerOption:
    opt = PickerOption(picker_id=picker_id, label=label, active=True)
    db.add(opt)
    db.commit()
    db.refresh(opt)
    return opt

def get_picker(db: Session, picker_id: int) -> Picker | None:
    return db.get(Picker, picker_id)

def list_options(db: Session, picker_id: int, active_only: bool = False) -> list[PickerOption]:
    stmt = select(PickerOption).where(PickerOption.picker_id == picker_id)
    if active_only:
        stmt = stmt.where(PickerOption.active.is_(True))
    stmt = stmt.order_by(PickerOption.id.asc())
    return list(db.scalars(stmt).all())

def add_event(db: Session, *, picker_id: int, picked_option_id: int | None, user_id: int | None,
              commit_hash: str, reveal_seed: str) -> PickEvent:
    ev = PickEvent(
        picker_id=picker_id,
        picked_option_id=picked_option_id,
        requested_by=user_id,
        commit_hash=commit_hash,
        reveal_seed=reveal_seed,
        algo_version="v1",
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

def list_events(db: Session, picker_id: int) -> list[PickEvent]:
    stmt = select(PickEvent).where(PickEvent.picker_id == picker_id).order_by(PickEvent.created_at.desc())
    return list(db.scalars(stmt).all())

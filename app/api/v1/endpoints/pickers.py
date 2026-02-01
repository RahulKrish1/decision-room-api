from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.dependencies_auth import get_current_user
from app.core.permissions import require_room_member
from app.crud.pickers import create_picker, add_option, get_picker, list_options, add_event, list_events
from app.schemas.pickers import (
    PickerCreateRequest, PickerOptionCreateRequest, PickerResponse,
    PickerOptionResponse, PickResponse, PickEventResponse
)
from app.services.picker_random import make_seed, sha256_hex, pick_index

router = APIRouter(tags=["pickers"])

@router.post("/rooms/{room_id}/pickers", response_model=PickerResponse, status_code=201)
def create(room_id: int, payload: PickerCreateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_room_member(room_id, db, user.id)
    picker = create_picker(db, room_id=room_id, user_id=user.id, name=payload.name)
    return PickerResponse(id=picker.id, room_id=picker.room_id, name=picker.name, options=[])

@router.post("/pickers/{picker_id}/options", response_model=PickerOptionResponse, status_code=201)
def add_opt(picker_id: int, payload: PickerOptionCreateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    picker = get_picker(db, picker_id)
    if not picker:
        raise HTTPException(status_code=404, detail="picker_not_found")
    require_room_member(picker.room_id, db, user.id)

    opt = add_option(db, picker_id=picker_id, label=payload.label)
    return PickerOptionResponse(id=opt.id, label=opt.label, active=opt.active)

@router.get("/pickers/{picker_id}", response_model=PickerResponse)
def get_one(picker_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    picker = get_picker(db, picker_id)
    if not picker:
        raise HTTPException(status_code=404, detail="picker_not_found")
    require_room_member(picker.room_id, db, user.id)

    opts = list_options(db, picker_id)
    return PickerResponse(
        id=picker.id, room_id=picker.room_id, name=picker.name,
        options=[PickerOptionResponse(id=o.id, label=o.label, active=o.active) for o in opts],
    )

@router.post("/pickers/{picker_id}/pick", response_model=PickResponse)
def pick(picker_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    picker = get_picker(db, picker_id)
    if not picker:
        raise HTTPException(status_code=404, detail="picker_not_found")
    require_room_member(picker.room_id, db, user.id)

    opts = list_options(db, picker_id, active_only=True)
    seed = make_seed()
    commit = sha256_hex(seed)

    if not opts:
        ev = add_event(db, picker_id=picker_id, picked_option_id=None, user_id=user.id, commit_hash=commit, reveal_seed=seed)
        return PickResponse(event_id=ev.id, picked_option_id=None, commit_hash=commit, reveal_seed=seed)

    idx = pick_index(seed, len(opts))
    picked = opts[idx]

    ev = add_event(db, picker_id=picker_id, picked_option_id=picked.id, user_id=user.id, commit_hash=commit, reveal_seed=seed)
    return PickResponse(event_id=ev.id, picked_option_id=picked.id, commit_hash=commit, reveal_seed=seed)

@router.get("/pickers/{picker_id}/history", response_model=list[PickEventResponse])
def history(picker_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    picker = get_picker(db, picker_id)
    if not picker:
        raise HTTPException(status_code=404, detail="picker_not_found")
    require_room_member(picker.room_id, db, user.id)

    events = list_events(db, picker_id)
    return [PickEventResponse(id=e.id, picked_option_id=e.picked_option_id, commit_hash=e.commit_hash, reveal_seed=e.reveal_seed) for e in events]

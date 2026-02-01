from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.dependencies_auth import get_current_user
from app.core.permissions import require_room_member
from app.crud.polls import create_poll, get_poll, list_polls_for_room, list_options, cast_vote, poll_results
from app.schemas.polls import PollCreateRequest, PollResponse, PollOptionResponse, VoteRequest, PollResultRow
from app.models.poll_option import PollOption

router = APIRouter(tags=["polls"])

@router.post("/rooms/{room_id}/polls", response_model=PollResponse, status_code=201)
def create_in_room(room_id: int, payload: PollCreateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_room_member(room_id, db, user.id)
    poll = create_poll(db, room_id=room_id, user_id=user.id, question=payload.question, options=payload.options)
    options = list_options(db, poll.id)
    return PollResponse(
        id=poll.id,
        room_id=poll.room_id,
        question=poll.question,
        status=poll.status,
        options=[PollOptionResponse(id=o.id, text=o.text, position=o.position) for o in options],
    )

@router.get("/rooms/{room_id}/polls", response_model=list[PollResponse])
def list_in_room(room_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_room_member(room_id, db, user.id)
    polls = list_polls_for_room(db, room_id)
    out = []
    for p in polls:
        opts = list_options(db, p.id)
        out.append(PollResponse(
            id=p.id, room_id=p.room_id, question=p.question, status=p.status,
            options=[PollOptionResponse(id=o.id, text=o.text, position=o.position) for o in opts],
        ))
    return out

@router.get("/polls/{poll_id}", response_model=PollResponse)
def get_one(poll_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    poll = get_poll(db, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="poll_not_found")
    require_room_member(poll.room_id, db, user.id)
    opts = list_options(db, poll_id)
    return PollResponse(
        id=poll.id, room_id=poll.room_id, question=poll.question, status=poll.status,
        options=[PollOptionResponse(id=o.id, text=o.text, position=o.position) for o in opts],
    )

@router.post("/polls/{poll_id}/vote", status_code=204)
def vote(poll_id: int, payload: VoteRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    poll = get_poll(db, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="poll_not_found")
    require_room_member(poll.room_id, db, user.id)

    # ensure option belongs to this poll
    opt = db.get(PollOption, payload.option_id)
    if not opt or opt.poll_id != poll_id:
        raise HTTPException(status_code=400, detail="invalid_option")

    cast_vote(db, poll_id=poll_id, option_id=payload.option_id, user_id=user.id)
    return None

@router.get("/polls/{poll_id}/results", response_model=list[PollResultRow])
def results(poll_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    poll = get_poll(db, poll_id)
    if not poll:
        raise HTTPException(status_code=404, detail="poll_not_found")
    require_room_member(poll.room_id, db, user.id)

    rows = poll_results(db, poll_id)
    return [PollResultRow(option_id=opt_id, votes=count) for (opt_id, count) in rows]

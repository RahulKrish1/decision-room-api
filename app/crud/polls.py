from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.poll import Poll
from app.models.poll_option import PollOption
from app.models.vote import Vote

def create_poll(db: Session, *, room_id: int, user_id: int, question: str, options: list[str]) -> Poll:
    poll = Poll(room_id=room_id, created_by=user_id, question=question, status="open")
    db.add(poll)
    db.flush()

    for idx, text in enumerate(options):
        db.add(PollOption(poll_id=poll.id, text=text, position=idx))

    db.commit()
    db.refresh(poll)
    return poll

def get_poll(db: Session, poll_id: int) -> Poll | None:
    return db.get(Poll, poll_id)

def list_polls_for_room(db: Session, room_id: int) -> list[Poll]:
    stmt = select(Poll).where(Poll.room_id == room_id).order_by(Poll.created_at.desc())
    return list(db.scalars(stmt).all())

def list_options(db: Session, poll_id: int) -> list[PollOption]:
    stmt = select(PollOption).where(PollOption.poll_id == poll_id).order_by(PollOption.position.asc())
    return list(db.scalars(stmt).all())

def cast_vote(db: Session, *, poll_id: int, option_id: int, user_id: int) -> None:
    # simplest behavior: upsert-like (delete previous then insert)
    existing = db.scalar(select(Vote).where(Vote.poll_id == poll_id, Vote.user_id == user_id))
    if existing:
        existing.option_id = option_id
        db.commit()
        return

    db.add(Vote(poll_id=poll_id, option_id=option_id, user_id=user_id))
    db.commit()

def poll_results(db: Session, poll_id: int) -> list[tuple[int, int]]:
    stmt = (
        select(Vote.option_id, func.count(Vote.id))
        .where(Vote.poll_id == poll_id)
        .group_by(Vote.option_id)
    )
    return [(row[0], row[1]) for row in db.execute(stmt).all()]

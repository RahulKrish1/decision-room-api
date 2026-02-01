from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class PickEvent(Base):
    __tablename__ = "pick_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    picker_id: Mapped[int] = mapped_column(ForeignKey("pickers.id", ondelete="CASCADE"), index=True, nullable=False)
    picked_option_id: Mapped[int] = mapped_column(ForeignKey("picker_options.id", ondelete="SET NULL"), nullable=True)

    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    commit_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    reveal_seed: Mapped[str] = mapped_column(String(64), nullable=False)

    algo_version: Mapped[str] = mapped_column(String(20), nullable=False, default="v1")
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

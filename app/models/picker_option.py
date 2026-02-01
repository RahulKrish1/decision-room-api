from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class PickerOption(Base):
    __tablename__ = "picker_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    picker_id: Mapped[int] = mapped_column(ForeignKey("pickers.id", ondelete="CASCADE"), index=True, nullable=False)

    label: Mapped[str] = mapped_column(String(120), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    weight: Mapped[int] = mapped_column(Integer, nullable=False, default=1)  # keep for future

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class SyncStatus(enum.Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class SyncState(Base):
    __tablename__ = "sync_state"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    last_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_sync_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    sync_status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus),
        nullable=False,
        default=SyncStatus.IDLE,
    )

    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.sync_state import SyncState, SyncStatus


class SyncStateRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_or_create(self) -> SyncState:
        result = await self._session.execute(select(SyncState).where(SyncState.id == 1))
        sync_state = result.scalar_one_or_none()

        if sync_state is not None:
            return sync_state

        sync_state = SyncState(id=1, sync_status=SyncStatus.IDLE)
        self._session.add(sync_state)
        await self._session.commit()
        await self._session.refresh(sync_state)
        return sync_state

    async def mark_running(self) -> SyncState:
        sync_state = await self.get_or_create()
        sync_state.sync_status = SyncStatus.RUNNING
        sync_state.last_sync_time = datetime.now(timezone.utc)
        sync_state.error_message = None
        await self._session.commit()
        await self._session.refresh(sync_state)
        return sync_state

    async def mark_success(self, last_changed_at) -> SyncState:
        sync_state = await self.get_or_create()
        sync_state.sync_status = SyncStatus.SUCCESS
        sync_state.last_sync_time = datetime.now(timezone.utc)
        sync_state.last_changed_at = last_changed_at
        sync_state.error_message = None
        await self._session.commit()
        await self._session.refresh(sync_state)
        return sync_state

    async def mark_failed(self, error_message: str) -> SyncState:
        sync_state = await self.get_or_create()
        sync_state.sync_status = SyncStatus.FAILED
        sync_state.last_sync_time = datetime.now(timezone.utc)
        sync_state.error_message = error_message
        await self._session.commit()
        await self._session.refresh(sync_state)
        return sync_state

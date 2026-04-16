from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.application.service.sync_events import SyncEventsService


class FakePaginator:
    def __init__(self, client, changed_at: str, events: list):
        self.client = client
        self.changed_at = changed_at
        self._events = list(events)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._events:
            raise StopAsyncIteration

        return self._events.pop(0)


@pytest.mark.asyncio
async def test_sync_first_run_success():
    client = object()
    first_event = SimpleNamespace(
        changed_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        place=SimpleNamespace(),
    )
    second_event = SimpleNamespace(
        changed_at=datetime(2026, 1, 3, 12, 0, tzinfo=UTC),
        place=SimpleNamespace(),
    )

    sync_state = SimpleNamespace(last_changed_at=None)
    place_repo = AsyncMock()
    event_repo = AsyncMock()
    sync_repo = AsyncMock()
    sync_repo.get_or_create.return_value = sync_state
    sync_repo.mark_running = AsyncMock(return_value=sync_state)
    sync_repo.mark_success = AsyncMock(return_value=sync_state)
    paginator_factory = Mock(
        return_value=FakePaginator(
            client=object(),
            changed_at="2000-01-01",
            events=[first_event, second_event],
        )
    )

    with (
        patch("src.application.service.sync_events.build_place_model") as mock_place,
        patch("src.application.service.sync_events.build_event_model") as mock_event,
    ):
        mock_place.side_effect = ["place-1", "place-2"]
        mock_event.side_effect = ["event-1", "event-2"]

        service = SyncEventsService(
            client=client,
            place_repository=place_repo,
            event_repository=event_repo,
            sync_state_repository=sync_repo,
            client_paginator=paginator_factory,
        )

        await service.sync()

    paginator_factory.assert_called_once_with(client, changed_at="2000-01-01")
    sync_repo.mark_running.assert_awaited_once()
    sync_repo.mark_success.assert_awaited_once_with(second_event.changed_at)
    assert place_repo.upsert.await_count == 2
    assert event_repo.upsert.await_count == 2


@pytest.mark.asyncio
async def test_sync_incremental_run_uses_last_changed_at_date():
    client = object()
    provider_event = SimpleNamespace(
        changed_at=datetime(2026, 2, 5, 9, 0, tzinfo=UTC),
        place=SimpleNamespace(),
    )
    sync_state = SimpleNamespace(
        last_changed_at=datetime(2026, 2, 1, 18, 30, tzinfo=UTC)
    )
    place_repo = AsyncMock()
    event_repo = AsyncMock()
    sync_repo = AsyncMock()
    sync_repo.get_or_create.return_value = sync_state
    sync_repo.mark_running = AsyncMock(return_value=sync_state)
    sync_repo.mark_success = AsyncMock(return_value=sync_state)
    paginator_factory = Mock(
        return_value=FakePaginator(
            client=object(),
            changed_at="2026-02-01",
            events=[provider_event],
        )
    )

    with (
        patch(
            "src.application.service.sync_events.build_place_model",
            return_value="place",
        ),
        patch(
            "src.application.service.sync_events.build_event_model",
            return_value="event",
        ),
    ):
        service = SyncEventsService(
            client=client,
            place_repository=place_repo,
            event_repository=event_repo,
            sync_state_repository=sync_repo,
            client_paginator=paginator_factory,
        )

        await service.sync()

    paginator_factory.assert_called_once_with(client, changed_at="2026-02-01")
    sync_repo.mark_success.assert_awaited_once_with(provider_event.changed_at)


@pytest.mark.asyncio
async def test_sync_marks_failed_on_error():
    client = object()
    provider_event = SimpleNamespace(
        changed_at=datetime(2026, 1, 1, tzinfo=UTC),
        place=SimpleNamespace(),
    )
    sync_state = SimpleNamespace(last_changed_at=None)
    place_repo = AsyncMock()
    place_repo.upsert.side_effect = RuntimeError("boom")
    event_repo = AsyncMock()
    sync_repo = AsyncMock()
    sync_repo.get_or_create.return_value = sync_state
    sync_repo.mark_running = AsyncMock(return_value=sync_state)
    sync_repo.mark_failed = AsyncMock(return_value=sync_state)
    paginator_factory = Mock(
        return_value=FakePaginator(
            client=object(),
            changed_at="2000-01-01",
            events=[provider_event],
        )
    )

    with (
        patch(
            "src.application.service.sync_events.build_place_model",
            return_value="place",
        ),
        patch(
            "src.application.service.sync_events.build_event_model",
            return_value="event",
        ),
    ):
        service = SyncEventsService(
            client=client,
            place_repository=place_repo,
            event_repository=event_repo,
            sync_state_repository=sync_repo,
            client_paginator=paginator_factory,
        )

        with pytest.raises(RuntimeError, match="boom"):
            await service.sync()

    sync_repo.mark_failed.assert_awaited_once_with("boom")


@pytest.mark.asyncio
async def test_sync_skips_events_with_unknown_status():
    client = object()
    provider_event = SimpleNamespace(
        status="archived",
        changed_at=datetime(2026, 1, 1, tzinfo=UTC),
        place=SimpleNamespace(),
    )
    sync_state = SimpleNamespace(last_changed_at=None)
    place_repo = AsyncMock()
    event_repo = AsyncMock()
    sync_repo = AsyncMock()
    sync_repo.get_or_create.return_value = sync_state
    sync_repo.mark_running = AsyncMock(return_value=sync_state)
    sync_repo.mark_success = AsyncMock(return_value=sync_state)
    paginator_factory = Mock(
        return_value=FakePaginator(
            client=object(),
            changed_at="2000-01-01",
            events=[provider_event],
        )
    )

    with (
        patch(
            "src.application.service.sync_events.build_place_model",
            return_value="place",
        ),
        patch(
            "src.application.service.sync_events.build_event_model", return_value=None
        ),
    ):
        service = SyncEventsService(
            client=client,
            place_repository=place_repo,
            event_repository=event_repo,
            sync_state_repository=sync_repo,
            client_paginator=paginator_factory,
        )

        await service.sync()

    place_repo.upsert.assert_awaited_once_with("place")
    event_repo.upsert.assert_not_awaited()
    sync_repo.mark_success.assert_awaited_once_with(provider_event.changed_at)

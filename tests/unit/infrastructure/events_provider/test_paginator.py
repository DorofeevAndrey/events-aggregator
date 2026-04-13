from unittest.mock import AsyncMock

import pytest

from src.infrastructure.events_provider.paginator import EventsPaginator


@pytest.mark.asyncio
async def test_paginator_yields_all_events():

    client = AsyncMock()

    client.events = AsyncMock(
        side_effect=[
            {
                "next": "http://test/api/events/?changed_at=2000-01-01&cursor=abc",
                "previous": None,
                "results": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "name": "Event 1",
                        "event_time": "2026-01-11T17:00:00+03:00",
                        "registration_deadline": "2026-01-10T17:00:00+03:00",
                        "status": "published",
                        "number_of_visitors": 5,
                        "changed_at": "2026-01-04T22:28:35.325270+03:00",
                        "created_at": "2026-01-04T22:28:35.325302+03:00",
                        "status_changed_at": "2026-01-04T22:28:35.325386+03:00",
                        "place": {
                            "id": "650e8400-e29b-41d4-a716-446655440001",
                            "name": "Place 1",
                            "city": "Moscow",
                            "address": "Street 1",
                            "seats_pattern": "A1-1000",
                            "changed_at": "2025-01-01T03:00:00+03:00",
                            "created_at": "2025-01-01T03:00:00+03:00",
                        },
                    }
                ],
            },
            {
                "next": None,
                "previous": "http://test/api/events/?changed_at=2000-01-01",
                "results": [],
            },
        ]
    )
    paginator = EventsPaginator(client, changed_at="2000-01-01")

    events = []
    async for event in paginator:
        events.append(event)

    assert len(events) == 1
    assert events[0].name == "Event 1"

    assert client.events.await_count == 2

    client.events.assert_any_await(
        changed_at="2000-01-01",
        cursor="abc",
    )


@pytest.mark.asyncio
async def test_paginator_stops_on_empty_page():
    client = AsyncMock()
    client.events = AsyncMock(
        return_value={"next": None, "previous": None, "results": []}
    )

    paginator = EventsPaginator(client, changed_at="2000-01-01")

    events = []
    async for event in paginator:
        events.append(event)

    assert events == []
    client.events.assert_awaited_once_with(changed_at="2000-01-01", cursor=None)

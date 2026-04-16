from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from src.infrastructure.events_provider.client import EventsProviderClient


@pytest.mark.asyncio
async def test_events_returns_json():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"next": None, "previous": None, "results": []}

    with patch(
        "src.infrastructure.events_provider.client.httpx.AsyncClient"
    ) as mock_async_client:
        mock_client = mock_async_client.return_value
        mock_client.__aenter__.return_value = mock_client

        mock_client.request = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        result = await client.events(changed_at="2000-01-01")

        assert result == {"next": None, "previous": None, "results": []}

        mock_client.request.assert_awaited_once_with(
            "GET",
            url="/api/events/",
            params={"changed_at": "2000-01-01"},
        )


@pytest.mark.asyncio
async def test_events_sends_cursor():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"next": None, "previous": None, "results": []}

    with patch(
        "src.infrastructure.events_provider.client.httpx.AsyncClient"
    ) as mock_async_client:
        mock_client = mock_async_client.return_value
        mock_client.request = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        await client.events(changed_at="2000-01-01", cursor="abc")

        mock_client.request.assert_awaited_once_with(
            "GET",
            url="/api/events/",
            params={"changed_at": "2000-01-01", "cursor": "abc"},
        )


@pytest.mark.asyncio
async def test_events_raises_http_error():
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="boom",
        request=Mock(),
        response=mock_response,
    )

    with patch(
        "src.infrastructure.events_provider.client.httpx.AsyncClient"
    ) as mock_async_client:
        mock_client = mock_async_client.return_value
        mock_client.request = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        with pytest.raises(httpx.HTTPStatusError):
            await client.events(changed_at="2000-01-01")


@pytest.mark.asyncio
async def test_events_retries_on_retryable_error_and_returns_json():
    failed_response = Mock()
    failed_response.status_code = 503
    failed_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="temporary failure",
        request=Mock(),
        response=failed_response,
    )

    success_response = Mock()
    success_response.raise_for_status.return_value = None
    success_response.json.return_value = {"next": None, "previous": None, "results": []}

    with (
        patch(
            "src.infrastructure.events_provider.client.httpx.AsyncClient"
        ) as mock_async_client,
        patch(
            "src.infrastructure.events_provider.client.asyncio.sleep", new=AsyncMock()
        ) as mock_sleep,
    ):
        mock_client = mock_async_client.return_value
        mock_client.request = AsyncMock(return_value=failed_response)
        mock_client.request.side_effect = [failed_response, success_response]

        client = EventsProviderClient("https://example.com", "api-key")

        result = await client.events(changed_at="2000-01-01")

        assert result == {"next": None, "previous": None, "results": []}
        assert mock_client.request.await_count == 2
        mock_sleep.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_ticket_returns_json_and_sends_payload():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "ticket_id": "1fed0122-b675-42e2-8ae7-49bfb53e8d7f"
    }

    with patch(
        "src.infrastructure.events_provider.client.httpx.AsyncClient"
    ) as mock_async_client:
        mock_client = mock_async_client.return_value
        mock_client.request = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        result = await client.create_ticket(
            event_id="550e8400-e29b-41d4-a716-446655440000",
            first_name="Ivan",
            last_name="Ivanov",
            email="ivan@example.com",
            seat="A15",
        )

        assert result == {"ticket_id": "1fed0122-b675-42e2-8ae7-49bfb53e8d7f"}
        mock_client.request.assert_awaited_once_with(
            "POST",
            url="/api/events/550e8400-e29b-41d4-a716-446655440000/register/",
            json={
                "first_name": "Ivan",
                "last_name": "Ivanov",
                "email": "ivan@example.com",
                "seat": "A15",
            },
        )


@pytest.mark.asyncio
async def test_delete_ticket_returns_json_and_sends_payload():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"success": True}

    with patch(
        "src.infrastructure.events_provider.client.httpx.AsyncClient"
    ) as mock_async_client:
        mock_client = mock_async_client.return_value
        mock_client.request = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        result = await client.delete_ticket(
            event_id="550e8400-e29b-41d4-a716-446655440000",
            ticket_id="1fed0122-b675-42e2-8ae7-49bfb53e8d7f",
        )

        assert result == {"success": True}

        mock_client.request.assert_awaited_once_with(
            "DELETE",
            url="/api/events/550e8400-e29b-41d4-a716-446655440000/unregister/",
            json={"ticket_id": "1fed0122-b675-42e2-8ae7-49bfb53e8d7f"},
        )


@pytest.mark.asyncio
async def test_seats_returns_json():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"seats": ["A1", "A2"]}

    with patch(
        "src.infrastructure.events_provider.client.httpx.AsyncClient"
    ) as mock_async_client:
        mock_client = mock_async_client.return_value
        mock_client.request = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        result = await client.seats(event_id="550e8400-e29b-41d4-a716-446655440000")

        assert result == {"seats": ["A1", "A2"]}

        mock_client.request.assert_awaited_once_with(
            "GET",
            url="/api/events/550e8400-e29b-41d4-a716-446655440000/seats/",
        )


@pytest.mark.asyncio
async def test_seats_raises_http_error():
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="boom",
        request=Mock(),
        response=mock_response,
    )

    with patch(
        "src.infrastructure.events_provider.client.httpx.AsyncClient"
    ) as mock_async_client:
        mock_client = mock_async_client.return_value
        mock_client.request = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        with pytest.raises(httpx.HTTPStatusError):
            await client.seats(event_id="550e8400-e29b-41d4-a716-446655440000")

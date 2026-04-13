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

        mock_client.get = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        result = await client.events(changed_at="2000-01-01")

        assert result == {"next": None, "previous": None, "results": []}

        mock_client.get.assert_awaited_once_with(
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
        mock_client.get = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        await client.events(changed_at="2000-01-01", cursor="abc")

        mock_client.get.assert_awaited_once_with(
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
        mock_client.get = AsyncMock(return_value=mock_response)

        client = EventsProviderClient("https://example.com", "api-key")

        with pytest.raises(httpx.HTTPStatusError):
            await client.events(changed_at="2000-01-01")

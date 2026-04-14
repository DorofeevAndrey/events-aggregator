import logging
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)


class EventsProviderClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"x-api-key": api_key},
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "EventsProviderClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def events(
        self, changed_at: str, cursor: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, str] = {"changed_at": changed_at}
        if cursor is not None:
            params["cursor"] = cursor

        try:
            response = await self._client.get(url="/api/events/", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                "Events API returned error",
                extra={
                    "status_code": e.response.status_code,
                    "params": params,
                },
            )
            raise

        return response.json()

    async def seats(self, event_id: UUID) -> dict[str, Any]:
        try:
            response = await self._client.get(url=f"/api/events/{event_id}/seats/")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                "Events seats API returned error",
                extra={
                    "status_code": e.response.status_code,
                    "event_id": event_id,
                },
            )
            raise

        return response.json()

    async def create_ticket(
        self, event_id: UUID, first_name: str, last_name: str, email: str, seat: str
    ) -> dict[str, str]:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }
        try:
            response = await self._client.post(
                url=f"/api/events/{event_id}/register/", json=payload
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                "Create ticket failed",
                extra={
                    "status_code": e.response.status_code,
                    "event_id": event_id,
                    "response_text": e.response.text,
                },
            )
            raise

        return response.json()

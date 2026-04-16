import asyncio
import logging
from typing import Any
from uuid import UUID

import httpx

logger = logging.getLogger(__name__)


class EventsProviderClient:
    _RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
    _MAX_RETRIES = 3

    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"x-api-key": api_key},
            timeout=timeout,
        )

    def _should_retry(self, error: httpx.HTTPStatusError | httpx.RequestError) -> bool:
        if isinstance(error, httpx.RequestError):
            return True

        return error.response.status_code in self._RETRYABLE_STATUS_CODES

    async def _sleep_before_retry(self, attempt: int) -> None:
        await asyncio.sleep(0.5 * (2 ** (attempt - 1)))

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **request_kwargs: Any,
    ) -> httpx.Response:
        last_error: Exception | None = None

        for attempt in range(1, self._MAX_RETRIES + 1):
            try:
                response = await self._client.request(method, url=url, **request_kwargs)
                response.raise_for_status()
                return response
            except (httpx.RequestError, httpx.HTTPStatusError) as error:
                last_error = error

                if attempt == self._MAX_RETRIES or not self._should_retry(error):
                    raise

                logger.warning(
                    "Events API request failed, retrying",
                    extra={
                        "attempt": attempt,
                        "max_retries": self._MAX_RETRIES,
                        "url": url,
                        "status_code": getattr(
                            getattr(error, "response", None), "status_code", None
                        ),
                    },
                )
                await self._sleep_before_retry(attempt)

        assert last_error is not None
        raise last_error

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
            response = await self._request_with_retry(
                "GET", url="/api/events/", params=params
            )
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
            response = await self._request_with_retry(
                "GET", url=f"/api/events/{event_id}/seats/"
            )
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
            response = await self._request_with_retry(
                "POST", url=f"/api/events/{event_id}/register/", json=payload
            )
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

    async def delete_ticket(self, event_id: UUID, ticket_id: UUID) -> dict[str, str]:
        try:
            payload: dict[str, str] = {"ticket_id": str(ticket_id)}
            response = await self._request_with_retry(
                "DELETE", url=f"/api/events/{event_id}/unregister/", json=payload
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                "Delete ticket failed",
                extra={
                    "status_code": e.response.status_code,
                    "event_id": event_id,
                },
            )
            raise

        return response.json()

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.exception_handlers import register_exception_handlers
from src.application.exceptions import EventNotFoundError, SeatUnavailableError


def test_domain_exception_handler_maps_to_http_status():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/event")
    async def raise_event_not_found():
        raise EventNotFoundError()

    client = TestClient(app)

    response = client.get("/event")

    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found"}


def test_domain_exception_handler_maps_seat_unavailable():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/seat")
    async def raise_seat_unavailable():
        raise SeatUnavailableError()

    client = TestClient(app)

    response = client.get("/seat")

    assert response.status_code == 400
    assert response.json() == {"detail": "Seat is unavailable"}

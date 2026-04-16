from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.exceptions import (
    ApplicationError,
    CannotCancelAfterEventPassedError,
    EmailAlreadyRegisteredError,
    EventNotFoundError,
    EventNotPublishedError,
    ProviderDidNotConfirmDeleteError,
    RegistrationClosedError,
    SeatUnavailableError,
    TicketDeletionRejectedError,
    TicketEventNotFoundError,
    TicketNotFoundError,
    TicketNotSyncedWithProviderError,
)

_EXCEPTION_DETAILS: dict[type[ApplicationError], tuple[int, str]] = {
    EventNotFoundError: (404, "Event not found"),
    EventNotPublishedError: (400, "Event is not published"),
    RegistrationClosedError: (400, "Registration is closed"),
    EmailAlreadyRegisteredError: (
        400,
        "This email is already registered for this event",
    ),
    SeatUnavailableError: (400, "Seat is unavailable"),
    TicketNotFoundError: (404, "Ticket not found"),
    TicketNotSyncedWithProviderError: (400, "Ticket not synced with provider"),
    TicketEventNotFoundError: (400, "Event with current ticket not found"),
    CannotCancelAfterEventPassedError: (400, "Cannot cancel after event has passed"),
    TicketDeletionRejectedError: (400, "Can't delete ticket"),
    ProviderDidNotConfirmDeleteError: (502, "Provider did not confirm delete"),
}


async def application_error_handler(request: Request, exc: ApplicationError):
    status_code, detail = _EXCEPTION_DETAILS[type(exc)]
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    app.exception_handler(ApplicationError)(application_error_handler)

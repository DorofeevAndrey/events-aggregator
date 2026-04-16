class ApplicationError(Exception):
    pass


class EventNotFoundError(ApplicationError):
    pass


class EventNotPublishedError(ApplicationError):
    pass


class RegistrationClosedError(ApplicationError):
    pass


class EmailAlreadyRegisteredError(ApplicationError):
    pass


class SeatUnavailableError(ApplicationError):
    pass


class TicketNotFoundError(ApplicationError):
    pass


class TicketNotSyncedWithProviderError(ApplicationError):
    pass


class TicketEventNotFoundError(ApplicationError):
    pass


class CannotCancelAfterEventPassedError(ApplicationError):
    pass


class TicketDeletionRejectedError(ApplicationError):
    pass


class ProviderDidNotConfirmDeleteError(ApplicationError):
    pass

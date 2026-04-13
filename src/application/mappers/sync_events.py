from datetime import UTC, datetime

from src.db.models.events import Event
from src.db.models.places import Place
from src.db.models.sync_state import SyncState, SyncStatus
from src.schemas.provider.provider_event import ProviderEventSchema


def build_place_model(provider_event: ProviderEventSchema) -> Place:
    return Place(
        id=provider_event.place.id,
        name=provider_event.place.name,
        city=provider_event.place.city,
        address=provider_event.place.address,
        seats_pattern=provider_event.place.seats_pattern,
        changed_at=provider_event.place.changed_at,
        created_at=provider_event.place.created_at,
    )


def build_event_model(provider_event: ProviderEventSchema) -> Event:
    return Event(
        id=provider_event.id,
        place_id=provider_event.place.id,
        name=provider_event.name,
        event_time=provider_event.event_time,
        registration_deadline=provider_event.registration_deadline,
        status=provider_event.status,
        number_of_visitors=provider_event.number_of_visitors,
        changed_at=provider_event.changed_at,
        created_at=provider_event.created_at,
        status_changed_at=provider_event.status_changed_at,
    )


def build_initial_sync_state() -> SyncState:
    return SyncState(
        id=1,
        last_changed_at=None,
        last_sync_time=datetime.now(UTC),
        sync_status=SyncStatus.RUNNING,
        error_message=None,
    )

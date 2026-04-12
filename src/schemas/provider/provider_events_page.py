from pydantic import BaseModel, ConfigDict

from src.schemas.provider.provider_event import ProviderEventSchema


class ProviderEventsPageSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    next: str | None
    previous: str | None
    results: list[ProviderEventSchema]

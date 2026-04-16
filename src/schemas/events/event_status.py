from enum import StrEnum


class EventStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    FINISHED = "finished"
    CANCELLED = "cancelled"

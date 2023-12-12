from datetime import datetime

from beanie import Document

__all__ = ("EMBEDDED_MESSAGE",)


class EMBEDDED_MESSAGE(Document):
    uuid: str
    author_id: int
    counts: dict[str, int]
    user_ids: dict[str, str]
    created_at: datetime
    attachment: str
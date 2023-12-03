import typing
from datetime import datetime

from beanie import Document, Indexed

__all__ = ("SINGLE_CHOICE_COMPONENT",)


class SINGLE_CHOICE_COMPONENT(Document):
    # name: typing.Annotated[str, Indexed(str)]
    # author_id: str
    # description: str
    # created_at: datetime
    # last_edited_at: typing.Optional[datetime] = None
    uuid: str
    author_id: int
    counts: dict[str, int]
    user_ids: dict[str, str]
    created_at: datetime

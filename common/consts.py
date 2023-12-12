import os
import typing
from pathlib import Path

import yaml

__all__ = ("SRC_PATH", "MetadataTyping", "METADATA", )

# we want to be absolutely sure this path is correct, so we
# do a bit of complicated path logic to get the src folder
SRC_PATH = Path(__file__).parent.parent.absolute().as_posix()


class MetadataTyping(typing.TypedDict):
    guild: int
    footer: str


METADATA_PATH = os.environ.get("METADATA_PATH", f"{SRC_PATH}/metadata.yml")
with open(METADATA_PATH, "r", encoding="utf-8") as file:
    METADATA: MetadataTyping = yaml.safe_load(file)

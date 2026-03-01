from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserId:
    value: UUID

    def __str__(self) -> str:
        return str(self.value)

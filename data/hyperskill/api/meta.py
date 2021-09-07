from dataclasses import dataclass


@dataclass
class Meta:
    page: int
    has_next: bool
    has_previous: bool

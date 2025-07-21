from dataclasses import dataclass
from typing import List

@dataclass
class Paper:
    doi: str
    title: str
    authors: List[str]
    summary: str

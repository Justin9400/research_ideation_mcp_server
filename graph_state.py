from dataclasses import dataclass
from typing import List, TypedDict

from paper import Paper

@dataclass
class GraphState(TypedDict):
    search_query: str
    max_retrievals: int
    papers: List[Paper]
    

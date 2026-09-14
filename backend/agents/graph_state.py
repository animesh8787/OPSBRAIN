from typing import TypedDict
from app.schemas import SearchResult, EquipmentNeighborhoodItem as EquipmentNode


class AgentState(TypedDict):
    query: str
    auth_token: str
    intent: str
    retrieved_chunks: list[SearchResult]
    graph_context: list[EquipmentNode] | None
    answer: str
    citations: list[dict]

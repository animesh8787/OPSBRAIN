# This is the only graph query schema for now. Named templates only — no raw SQL/Cypher passthrough is ever exposed to the client.

from pydantic import BaseModel


class EquipmentNeighborhoodRequest(BaseModel):
    tag: str
    max_depth: int = 2


class EquipmentNeighborhoodItem(BaseModel):
    tag_number: str
    failures: list[str]
    regulations: list[str]


class EquipmentConnectionItem(BaseModel):
    from_tag: str
    to_tag: str


class EquipmentNeighborhoodResponse(BaseModel):
    equipment: list[EquipmentNeighborhoodItem]
    connections: list[EquipmentConnectionItem]

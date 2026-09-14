from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.postgres import get_db
from app.db.postgres.models import User
from app.schemas import EquipmentNeighborhoodRequest, EquipmentNeighborhoodResponse
from app.services.graph_service import get_equipment_neighborhood_with_connections

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.post("/query", response_model=EquipmentNeighborhoodResponse)
async def query_equipment_neighborhood(
    payload: EquipmentNeighborhoodRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    equipment, connections = await get_equipment_neighborhood_with_connections(
        db, tag=payload.tag, max_depth=payload.max_depth
    )
    return EquipmentNeighborhoodResponse(equipment=equipment, connections=connections)

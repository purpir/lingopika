from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.hearts_service import get_hearts, regen_hearts
from app.schemas.schemas import HeartsOut

router = APIRouter(prefix="/hearts", tags=["hearts"])


@router.get("", response_model=HeartsOut)
async def hearts(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    h = await get_hearts(db, user)
    await db.commit()
    out = HeartsOut.model_validate(h)
    if h.next_regen_at:
        out.seconds_to_next = max(0, int((h.next_regen_at - __import__("datetime").datetime.now(__import__("datetime").timezone.utc)).total_seconds()))
    return out

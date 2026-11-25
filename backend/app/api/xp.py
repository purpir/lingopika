from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.xp_service import xp_to_next_level
from app.schemas.schemas import XPTransactionOut

router = APIRouter(prefix="/xp", tags=["xp"])


@router.get("/history")
async def history(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from sqlalchemy import select
    from app.db.models import XPTransaction
    res = await db.execute(select(XPTransaction).where(XPTransaction.user_id == user.id).order_by(XPTransaction.created_at.desc()).limit(50))
    return [XPTransactionOut.model_validate(x) for x in res.scalars().all()]

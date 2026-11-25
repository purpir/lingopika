from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.config import settings
from app.services.premium_service import PLANS, get_premium_status
from app.schemas.schemas import PremiumPlan, CreateInvoiceRequest, CreateInvoiceResponse, PremiumStatus
from aiogram import Bot
from aiogram.types import LabeledPrice

router = APIRouter(prefix="/premium", tags=["premium"])


@router.get("/plans", response_model=list[PremiumPlan])
async def plans():
    out = []
    for pid, info in PLANS.items():
        out.append(PremiumPlan(id=pid, title=info["title"], stars=info["stars"], duration_days=info["days"], description=info["description"], best_value=(pid == "monthly")))
    return out


@router.get("/status", response_model=PremiumStatus)
async def status(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    st = await get_premium_status(db, user)
    await db.commit()
    return PremiumStatus(**st)


@router.post("/invoice", response_model=CreateInvoiceResponse)
async def create_invoice(payload: CreateInvoiceRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if payload.plan not in PLANS:
        raise HTTPException(400, "Unknown plan")
    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(500, "Bot token not configured")
    info = PLANS[payload.plan]
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    try:
        link = await bot.create_invoice_link(
            title=info["title"],
            description=info["description"],
            payload=f"premium:{payload.plan}:{user.telegram_id}",
            provider_token=settings.STARS_PROVIDER_TOKEN or "",
            currency="XTR",
            prices=[LabeledPrice(label=info["title"], amount=info["stars"])],
        )
    finally:
        await bot.session.close()
    return CreateInvoiceResponse(invoice_link=link)

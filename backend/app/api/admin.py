from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.api.deps import require_admin
from app.db.models import User, Lesson, Word, Payment, UserProfile
from app.schemas.schemas import AdminUserOut, AdminStats

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
async def stats(db: AsyncSession = Depends(get_db), admin=Depends(require_admin)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    premium_users = (await db.execute(select(func.count(UserProfile.id)).where(UserProfile.is_premium == True))).scalar() or 0
    total_lessons = (await db.execute(select(func.count(Lesson.id)))).scalar() or 0
    total_words = (await db.execute(select(func.count(Word.id)))).scalar() or 0
    total_payments = (await db.execute(select(func.count(Payment.id)))).scalar() or 0
    return AdminStats(total_users=total_users, premium_users=premium_users, total_lessons=total_lessons, total_words=total_words, total_payments=total_payments)


@router.get("/users", response_model=list[AdminUserOut])
async def users(db: AsyncSession = Depends(get_db), admin=Depends(require_admin)):
    res = await db.execute(select(User).order_by(User.created_at.desc()).limit(200))
    out = []
    for u in res.scalars().all():
        profile = u.profile
        out.append(AdminUserOut(id=u.id, telegram_id=u.telegram_id, username=u.username, first_name=u.first_name, english_level=profile.english_level if profile else None, total_xp=profile.total_xp if profile else 0, is_premium=profile.is_premium if profile else False, created_at=u.created_at))
    return out

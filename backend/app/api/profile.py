from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.hearts_service import get_hearts
from app.services.streak_service import record_activity
from app.services.premium_service import check_premium_expiry
from app.schemas.schemas import ProfileOut, UserOut, UserProfileOut, HeartsOut, StreakOut, UserSettingsOut

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
async def profile(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await check_premium_expiry(db, user)
    hearts = await get_hearts(db, user)
    await db.commit()
    profile = user.profile
    xp_next = (profile.level) * 100 - profile.total_xp
    profile_out = UserProfileOut.model_validate(profile)
    profile_out.xp_to_next_level = max(0, xp_next)
    streak_out = StreakOut.model_validate(user.streak) if user.streak else StreakOut(current_streak=0, longest_streak=0, total_active_days=0)
    hearts_out = HeartsOut.model_validate(hearts)
    if hearts.next_regen_at:
        import datetime as dt
        hearts_out.seconds_to_next = max(0, int((hearts.next_regen_at - dt.datetime.now(dt.timezone.utc)).total_seconds()))
    settings_out = UserSettingsOut.model_validate(user.settings)
    return ProfileOut(user=UserOut.model_validate(user), profile=profile_out, hearts=hearts_out, streak=streak_out, settings=settings_out)


@router.post("/onboarding")
async def onboarding(level: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    from app.services.user_service import set_onboarding
    await set_onboarding(db, user, level)
    await db.commit()
    return {"ok": True}

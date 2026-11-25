from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schemas.schemas import UserSettingsOut, UserSettingsUpdate
from app.services.streak_service import record_activity

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/settings", response_model=UserSettingsOut)
async def update_settings(payload: UserSettingsUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    s = user.settings
    if payload.notifications_enabled is not None:
        s.notifications_enabled = payload.notifications_enabled
    if payload.reminder_hour is not None:
        s.reminder_hour = payload.reminder_hour
    if payload.timezone is not None:
        s.timezone = payload.timezone
    if payload.theme is not None:
        s.theme = payload.theme
    await db.commit()
    return UserSettingsOut.model_validate(s)


@router.post("/activity")
async def activity(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    streak = await record_activity(db, user)
    await db.commit()
    return {"current_streak": streak.current_streak}

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.services.league_service import ensure_participation, get_league_status, finalize_season_if_expired, add_weekly_xp
from app.schemas.schemas import LeagueStatus

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.get("/status", response_model=LeagueStatus)
async def status(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    await finalize_season_if_expired(db, user)
    st = await get_league_status(db, user)
    await db.commit()
    # convert participants to schema
    from app.schemas.schemas import LeagueParticipantOut, LeagueOut
    parts = [LeagueParticipantOut(id=p["id"], name=p["name"], avatar=p["avatar"], weekly_xp=p["weekly_xp"], position=p["position"], is_bot=p["is_bot"], is_user=p["is_user"]) for p in st["participants"]]
    league = LeagueOut(id=st["league"]["id"], slug=st["league"]["slug"], name=st["league"]["name"], tier=st["league"]["tier"])
    return LeagueStatus(league=league, season_end_at=st["season_end_at"], seconds_to_end=st["seconds_to_end"], user_position=st["user_position"], user_weekly_xp=st["user_weekly_xp"], promotion_zone=st["promotion_zone"], demotion_zone=st["demotion_zone"], participants=parts)

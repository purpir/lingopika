from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import League, LeagueSeason, LeagueBot, LeagueParticipant, User, UserProfile

def _aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def get_or_create_active_season(db: AsyncSession, league: League) -> LeagueSeason:
    now = datetime.now(timezone.utc)
    res = await db.execute(select(LeagueSeason).where(LeagueSeason.league_id == league.id, LeagueSeason.is_active == True, LeagueSeason.end_at > now))
    season = res.scalar_one_or_none()
    if season:
        return season
    # create new
    season = LeagueSeason(league_id=league.id, start_at=now, end_at=now + timedelta(days=7), is_active=True)
    db.add(season)
    await db.flush()
    return season


async def ensure_participation(db: AsyncSession, user: User) -> LeagueParticipant:
    # find user's latest active participation
    now = datetime.now(timezone.utc)
    res = await db.execute(
        select(LeagueParticipant).join(LeagueSeason).where(LeagueParticipant.user_id == user.id, LeagueSeason.is_active == True, LeagueSeason.end_at > now)
    )
    part = res.scalar_one_or_none()
    if part:
        return part
    # determine league: bronze for new
    league = (await db.execute(select(League).where(League.slug == "bronze"))).scalar_one_or_none()
    if not league:
        # create leagues if missing
        await seed_leagues(db)
        league = (await db.execute(select(League).where(League.slug == "bronze"))).scalar_one_or_none()
    season = await get_or_create_active_season(db, league)
    # add bots
    bots = (await db.execute(select(LeagueBot).where(LeagueBot.league_id == league.id))).scalars().all()
    for b in bots[:29]:
        exists = (await db.execute(select(LeagueParticipant).where(LeagueParticipant.season_id == season.id, LeagueParticipant.bot_id == b.id))).scalar_one_or_none()
        if not exists:
            bp = LeagueParticipant(season_id=season.id, bot_id=b.id, is_bot=True, weekly_xp=0)
            db.add(bp)
    # user
    part = LeagueParticipant(season_id=season.id, user_id=user.id, is_bot=False, weekly_xp=0)
    db.add(part)
    await db.flush()
    return part


async def seed_leagues(db: AsyncSession):
    names = [("bronze", "Bronze", 1), ("silver", "Silver", 2), ("gold", "Gold", 3), ("platinum", "Platinum", 4), ("diamond", "Diamond", 5), ("master", "Master", 6)]
    for slug, name, tier in names:
        exists = (await db.execute(select(League).where(League.slug == slug))).scalar_one_or_none()
        if not exists:
            db.add(League(slug=slug, name=name, tier=tier, promotion_count=5, demotion_count=5, max_participants=30))
    await db.flush()
    # seed bots for bronze if none
    bronze = (await db.execute(select(League).where(League.slug == "bronze"))).scalar_one_or_none()
    if bronze:
        cnt = (await db.execute(select(func.count(LeagueBot.id)).where(LeagueBot.league_id == bronze.id))).scalar() or 0
        if cnt == 0:
            import random
            names_bots = ["Alex", "Maria", "John", "Emma", "Leo", "Sofia", "Max", "Anna", "Tom", "Kate", "Ryan", "Lily", "Dan", "Nina", "Sam", "Ivy", "Chris", "Zoe", "Mike", "Eva", "Ben", "Mia", "Jack", "Amy", "Luke", "Rose", "Nick", "Luna", "Ray"]
            avatars = ["🦊", "🐼", "🐨", "🐯", "🐸", "🐵", "🐰", "🐱"]
            for i, n in enumerate(names_bots):
                db.add(LeagueBot(name=n, avatar=random.choice(avatars), level=random.randint(1, 5), base_xp_per_week=random.randint(80, 250), activity_factor=round(random.uniform(0.7, 1.3), 2), league_id=bronze.id))
    await db.flush()


async def add_weekly_xp(db: AsyncSession, user: User, amount: int):
    if amount <= 0:
        return
    part = await ensure_participation(db, user)
    part.weekly_xp += amount
    await db.flush()
    # also simulate bot progress? done in status
    await simulate_bot_progress(db, part.season_id)


async def simulate_bot_progress(db: AsyncSession, season_id: int):
    # add small random xp to bots occasionally (deterministic-ish by time)
    import random
    parts = (await db.execute(select(LeagueParticipant).where(LeagueParticipant.season_id == season_id, LeagueParticipant.is_bot == True))).scalars().all()
    for p in parts:
        bot = (await db.execute(select(LeagueBot).where(LeagueBot.id == p.bot_id))).scalar_one_or_none()
        if bot:
            # add xp based on base per week / 7 / 24 roughly, but only sometimes
            increment = int(bot.base_xp_per_week * bot.activity_factor / 7 / 6)  # ~4 updates/day
            if random.random() < 0.3:
                p.weekly_xp += increment
    await db.flush()


async def get_league_status(db: AsyncSession, user: User) -> dict:
    part = await ensure_participation(db, user)
    season = (await db.execute(select(LeagueSeason).where(LeagueSeason.id == part.season_id))).scalar_one_or_none()
    league = (await db.execute(select(League).where(League.id == season.league_id))).scalar_one_or_none()
    # participants
    all_parts = (await db.execute(select(LeagueParticipant).where(LeagueParticipant.season_id == season.id))).scalars().all()
    # build list with names
    rows = []
    for p in all_parts:
        if p.is_bot:
            bot = (await db.execute(select(LeagueBot).where(LeagueBot.id == p.bot_id))).scalar_one_or_none()
            name = bot.name if bot else "Bot"
            avatar = bot.avatar if bot else "🤖"
        else:
            u = (await db.execute(select(User).where(User.id == p.user_id))).scalar_one_or_none()
            name = (u.first_name or u.username or "You") if u else "You"
            avatar = "👤"
        rows.append({"id": p.id, "name": name, "avatar": avatar, "weekly_xp": p.weekly_xp, "is_bot": p.is_bot, "is_user": (p.user_id == user.id)})
    rows.sort(key=lambda r: r["weekly_xp"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["position"] = i
    user_row = next((r for r in rows if r["is_user"]), None)
    now = datetime.now(timezone.utc)
    seconds_to_end = int((season.end_at - now).total_seconds()) if season.end_at > now else 0
    # promotion/demotion zones
    total = len(rows)
    promo = league.promotion_count
    demo = league.demotion_count
    return {
        "league": {"id": league.id, "slug": league.slug, "name": league.name, "tier": league.tier},
        "season_end_at": season.end_at,
        "seconds_to_end": seconds_to_end,
        "user_position": user_row["position"] if user_row else None,
        "user_weekly_xp": user_row["weekly_xp"] if user_row else 0,
        "promotion_zone": promo,
        "demotion_zone": demo,
        "participants": rows,
    }


async def finalize_season_if_expired(db: AsyncSession, user: User):
    part = await ensure_participation(db, user)
    season = (await db.execute(select(LeagueSeason).where(LeagueSeason.id == part.season_id))).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if season and season.end_at <= now and season.is_active:
        # finalize
        season.is_active = False
        # determine user position
        status = await get_league_status(db, user)
        pos = status["user_position"]
        total = len(status["participants"])
        league = (await db.execute(select(League).where(League.id == season.league_id))).scalar_one_or_none()
        # reward hearts for top 3
        from app.services.hearts_service import refill_hearts
        if pos == 1:
            await refill_hearts(db, user, 3)
        elif pos == 2:
            await refill_hearts(db, user, 2)
        elif pos == 3:
            await refill_hearts(db, user, 1)
        # promotion/demotion
        promo = league.promotion_count
        demo = league.demotion_count
        idx = LEAGUE_ORDER.index(league.slug)
        target_slug = league.slug
        if pos is not None and pos <= promo and idx < len(LEAGUE_ORDER) - 1:
            target_slug = LEAGUE_ORDER[idx + 1]
        elif pos is not None and pos > total - demo and idx > 0:
            target_slug = LEAGUE_ORDER[idx - 1]
        # create next participation
        target_league = (await db.execute(select(League).where(League.slug == target_slug))).scalar_one_or_none()
        if target_league:
            new_season = await get_or_create_active_season(db, target_league)
            # add bots if needed
            bots = (await db.execute(select(LeagueBot).where(LeagueBot.league_id == target_league.id))).scalars().all()
            if not bots:
                # reuse bronze bots? just skip
                pass
            for b in bots[:29]:
                exists = (await db.execute(select(LeagueParticipant).where(LeagueParticipant.season_id == new_season.id, LeagueParticipant.bot_id == b.id))).scalar_one_or_none()
                if not exists:
                    db.add(LeagueParticipant(season_id=new_season.id, bot_id=b.id, is_bot=True, weekly_xp=0))
            # user participation if not exists
            exists_up = (await db.execute(select(LeagueParticipant).where(LeagueParticipant.season_id == new_season.id, LeagueParticipant.user_id == user.id))).scalar_one_or_none()
            if not exists_up:
                db.add(LeagueParticipant(season_id=new_season.id, user_id=user.id, is_bot=False, weekly_xp=0))
        await db.flush()
        # create notification
        from app.db.models import Notification
        db.add(Notification(user_id=user.id, type="league_end", title="Season ended", body=f"You finished #{pos} in {league.name} league!"))
        await db.flush()
    return

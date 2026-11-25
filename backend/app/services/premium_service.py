from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User, Subscription, Payment
def _aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

PLANS = {
    "weekly": {"title": "Premium Weekly", "stars": 49, "days": 7, "description": "7 days of unlimited hearts and premium lessons"},
    "monthly": {"title": "Premium Monthly", "stars": 149, "days": 30, "description": "30 days — best value, save 47 Stars"},
}


def plan_info(plan: str) -> dict:
    return PLANS[plan]


async def activate_premium(db: AsyncSession, user: User, plan: str, charge_id: str, provider_charge_id: str | None = None, raw: dict | None = None) -> Subscription:
    # idempotency: if payment already exists, return
    existing = (await db.execute(select(Payment).where(Payment.telegram_payment_charge_id == charge_id))).scalar_one_or_none()
    if existing:
        # already processed
        sub = None
        if existing.subscription_id:
            sub = (await db.execute(select(Subscription).where(Subscription.id == existing.subscription_id))).scalar_one_or_none()
        return sub
    info = PLANS[plan]
    now = datetime.now(timezone.utc)
    days = info["days"]
    expires = now + timedelta(days=days)
    # extend existing premium if active
    profile = user.profile
    if profile.is_premium and profile.premium_until and profile.premium_until > now:
        expires = profile.premium_until + timedelta(days=days)
    sub = Subscription(user_id=user.id, plan=plan, status="active", started_at=now, expires_at=expires, telegram_charge_id=charge_id)
    db.add(sub)
    await db.flush()
    payment = Payment(user_id=user.id, subscription_id=sub.id, plan=plan, amount_stars=info["stars"], telegram_payment_charge_id=charge_id, provider_payment_charge_id=provider_charge_id, status="completed", raw_payload=raw)
    db.add(payment)
    await db.flush()
    profile.is_premium = True
    profile.premium_until = expires
    # hearts infinite: set count to max and no regen
    from app.services.hearts_service import get_hearts
    hearts = await get_hearts(db, user)
    hearts.count = hearts.max_count
    hearts.next_regen_at = None
    await db.flush()
    return sub


async def check_premium_expiry(db: AsyncSession, user: User):
    profile = user.profile
    if profile.is_premium and profile.premium_until:
        if datetime.now(timezone.utc) >= _aware(profile.premium_until):
            profile.is_premium = False
            subs = (await db.execute(select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active"))).scalars().all()
            for s in subs:
                if _aware(s.expires_at) <= datetime.now(timezone.utc):
                    s.status = "expired"
            await db.flush()


async def get_premium_status(db: AsyncSession, user: User) -> dict:
    await check_premium_expiry(db, user)
    profile = user.profile
    plan = None
    if profile.is_premium:
        sub = (await db.execute(select(Subscription).where(Subscription.user_id == user.id, Subscription.status == "active").order_by(Subscription.created_at.desc()))).scalar_one_or_none()
        plan = sub.plan if sub else None
    return {"is_premium": profile.is_premium, "premium_until": profile.premium_until, "plan": plan}

from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Word, UserWord, User, Lesson

async def ensure_words_for_lesson(db: AsyncSession, user: User, lesson_id: int):
    words = (await db.execute(select(Word).where(Word.lesson_id == lesson_id))).scalars().all()
    for w in words:
        existing = (await db.execute(select(UserWord).where(UserWord.user_id == user.id, UserWord.word_id == w.id))).scalar_one_or_none()
        if not existing:
            uw = UserWord(user_id=user.id, word_id=w.id, status="new", next_review_at=datetime.now(timezone.utc))
            db.add(uw)
    await db.flush()


def _srs_update(uw: UserWord, known: bool):
    now = datetime.now(timezone.utc)
    if known:
        uw.repetitions += 1
        if uw.repetitions == 1:
            uw.interval_days = 1
        elif uw.repetitions == 2:
            uw.interval_days = 3
        else:
            uw.interval_days = int(round(uw.interval_days * uw.ease_factor))
        uw.ease_factor = min(3.0, uw.ease_factor + 0.1)
        uw.times_correct += 1
        uw.status = "known" if uw.repetitions >= 3 else "learning"
    else:
        uw.repetitions = 0
        uw.interval_days = 1
        uw.ease_factor = max(1.3, uw.ease_factor - 0.2)
        uw.times_wrong += 1
        uw.status = "learning"
    uw.last_reviewed_at = now
    uw.next_review_at = now + timedelta(days=uw.interval_days)


async def review_word(db: AsyncSession, user: User, word_id: int, known: bool, idempotency_key: str | None = None) -> UserWord:
    uw = (await db.execute(select(UserWord).where(UserWord.user_id == user.id, UserWord.word_id == word_id))).scalar_one_or_none()
    if not uw:
        # create
        uw = UserWord(user_id=user.id, word_id=word_id, status="new")
        db.add(uw)
        await db.flush()
    _srs_update(uw, known)
    await db.flush()
    # load word
    await db.refresh(uw)
    return uw


async def get_due_cards(db: AsyncSession, user: User, limit: int = 20) -> list[UserWord]:
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(UserWord).where(UserWord.user_id == user.id, (UserWord.next_review_at == None) | (UserWord.next_review_at <= now)).order_by(UserWord.next_review_at).limit(limit)
    )
    return list(result.scalars().all())


async def get_new_cards(db: AsyncSession, user: User, limit: int = 20) -> list[UserWord]:
    result = await db.execute(select(UserWord).where(UserWord.user_id == user.id, UserWord.status == "new").limit(limit))
    return list(result.scalars().all())


async def vocabulary_stats(db: AsyncSession, user: User) -> dict:
    total = (await db.execute(select(func.count(UserWord.id)).where(UserWord.user_id == user.id))).scalar() or 0
    new = (await db.execute(select(func.count(UserWord.id)).where(UserWord.user_id == user.id, UserWord.status == "new"))).scalar() or 0
    learning = (await db.execute(select(func.count(UserWord.id)).where(UserWord.user_id == user.id, UserWord.status == "learning"))).scalar() or 0
    known = (await db.execute(select(func.count(UserWord.id)).where(UserWord.user_id == user.id, UserWord.status == "known"))).scalar() or 0
    now = datetime.now(timezone.utc)
    due = (await db.execute(select(func.count(UserWord.id)).where(UserWord.user_id == user.id, (UserWord.next_review_at == None) | (UserWord.next_review_at <= now)))).scalar() or 0
    return {"total": total, "new": new, "learning": learning, "known": known, "due_for_review": due}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import Word, UserWord
from app.services.card_service import get_due_cards, get_new_cards, review_word, vocabulary_stats
from app.schemas.schemas import UserWordOut, WordOut, CardReviewRequest, VocabularyStats

router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("/due", response_model=list[UserWordOut])
async def due(limit: int = 20, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    uws = await get_due_cards(db, user, limit)
    out = []
    for uw in uws:
        w = (await db.execute(select(Word).where(Word.id == uw.word_id))).scalar_one()
        uo = UserWordOut.model_validate(uw)
        uo.word = WordOut.model_validate(w)
        out.append(uo)
    await db.commit()
    return out


@router.get("/new", response_model=list[UserWordOut])
async def new(limit: int = 20, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    uws = await get_new_cards(db, user, limit)
    out = []
    for uw in uws:
        w = (await db.execute(select(Word).where(Word.id == uw.word_id))).scalar_one()
        uo = UserWordOut.model_validate(uw)
        uo.word = WordOut.model_validate(w)
        out.append(uo)
    await db.commit()
    return out


@router.post("/review")
async def review(payload: CardReviewRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    uw = await review_word(db, user, payload.word_id, payload.known, payload.idempotency_key)
    await db.commit()
    return {"status": uw.status, "next_review_at": uw.next_review_at}


@router.get("/stats", response_model=VocabularyStats)
async def stats(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    s = await vocabulary_stats(db, user)
    await db.commit()
    return VocabularyStats(**s)

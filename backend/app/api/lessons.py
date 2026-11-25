from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import Lesson, Exercise
from app.services.course_service import get_lesson, can_access_lesson, start_lesson
from app.services.lesson_service import complete_lesson
from app.services.exercise_service import submit_answer
from app.services.card_service import ensure_words_for_lesson
from app.schemas.schemas import LessonDetail, LessonOut, ExerciseOut, AnswerSubmit, AnswerResult, LessonCompleteRequest

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=LessonDetail)
async def lesson_detail(lesson_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    lesson = await get_lesson(db, lesson_id)
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    if not can_access_lesson(user, lesson):
        raise HTTPException(403, "Premium required")
    exercises = (await db.execute(select(Exercise).where(Exercise.lesson_id == lesson_id).order_by(Exercise.order_index))).scalars().all()
    lo = LessonOut.model_validate(lesson)
    return LessonDetail(lesson=lo, exercises=[ExerciseOut.model_validate(e) for e in exercises])


@router.post("/{lesson_id}/start")
async def start(lesson_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    lesson = await get_lesson(db, lesson_id)
    if not lesson or not can_access_lesson(user, lesson):
        raise HTTPException(403, "Access denied")
    prog = await start_lesson(db, user, lesson_id)
    await ensure_words_for_lesson(db, user, lesson_id)
    await db.commit()
    return {"status": prog.status}


@router.post("/answer", response_model=AnswerResult)
async def answer(payload: AnswerSubmit, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        res = await submit_answer(db, user, payload.exercise_id, payload.answer, payload.idempotency_key)
    except ValueError as e:
        raise HTTPException(400, str(e))
    await db.commit()
    return AnswerResult(**res)


@router.post("/complete")
async def complete(payload: LessonCompleteRequest, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    try:
        res = await complete_lesson(db, user, payload.lesson_id, payload.idempotency_key)
    except ValueError as e:
        raise HTTPException(400, str(e))
    await db.commit()
    return res

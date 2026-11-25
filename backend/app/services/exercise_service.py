from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Exercise, Lesson, ExerciseAttempt, User, LessonProgress
from app.services.hearts_service import spend_heart, get_hearts
from app.services.xp_service import award_xp
from app.services.course_service import can_access_lesson
from app.config import settings


import re


def normalize(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[.,!?]+$", "", s)  # убрать завершающие знаки препинания
    return " ".join(s.split())


async def submit_answer(db: AsyncSession, user: User, exercise_id: int, answer: str, idempotency_key: str | None = None) -> dict:
    # idempotency check
    if idempotency_key:
        res = await db.execute(select(ExerciseAttempt).where(ExerciseAttempt.idempotency_key == idempotency_key))
        existing = res.scalar_one_or_none()
        if existing:
            hearts = await get_hearts(db, user)
            return {
                "is_correct": existing.is_correct,
                "correct_answer": None,
                "explanation": None,
                "xp_awarded": existing.xp_awarded,
                "hearts_remaining": hearts.count if not user.profile.is_premium else None,
                "lesson_completed": False,
            }

    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise ValueError("Exercise not found")
    lesson = await db.execute(select(Lesson).where(Lesson.id == exercise.lesson_id))
    lesson = lesson.scalar_one_or_none()
    if not lesson or not can_access_lesson(user, lesson):
        raise ValueError("Access denied")

    is_correct = normalize(answer) == normalize(exercise.correct_answer)
    xp_awarded = 0
    if is_correct:
        xp_awarded = await award_xp(db, user, exercise.xp_reward, "exercise", source_id=str(exercise.id), idempotency_key=f"ex:{exercise.id}:{user.id}:{idempotency_key or answer}")
    else:
        # spend heart (unless premium)
        if not user.profile.is_premium:
            await spend_heart(db, user, 1)

    attempt = ExerciseAttempt(
        user_id=user.id,
        exercise_id=exercise.id,
        lesson_id=lesson.id,
        answer=answer,
        is_correct=is_correct,
        xp_awarded=xp_awarded,
        idempotency_key=idempotency_key,
    )
    db.add(attempt)
    await db.flush()

    hearts = await get_hearts(db, user)
    hearts_remaining = hearts.count if not user.profile.is_premium else None

    # check lesson completion: all exercises attempted correctly? Simplify: mark completed when user calls complete; here just return
    return {
        "is_correct": is_correct,
        "correct_answer": exercise.correct_answer if not is_correct else None,
        "explanation": exercise.explanation,
        "xp_awarded": xp_awarded,
        "hearts_remaining": hearts_remaining,
        "lesson_completed": False,
    }

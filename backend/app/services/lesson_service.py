from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from app.db.models import Lesson, LessonProgress, User
from app.services.xp_service import award_xp
from app.services.streak_service import record_activity
from app.services.course_service import can_access_lesson


async def complete_lesson(db: AsyncSession, user: User, lesson_id: int, idempotency_key: str | None = None) -> dict:
    lesson = (await db.execute(select(Lesson).where(Lesson.id == lesson_id))).scalar_one_or_none()
    if not lesson or not can_access_lesson(user, lesson):
        raise ValueError("Access denied")
    prog = (await db.execute(select(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id))).scalar_one_or_none()
    if not prog:
        prog = LessonProgress(user_id=user.id, lesson_id=lesson_id, status="in_progress", started_at=datetime.now(timezone.utc))
        db.add(prog)
        await db.flush()
    already = prog.status == "completed"
    xp_awarded = 0
    if not already:
        prog.status = "completed"
        prog.completed_at = datetime.now(timezone.utc)
        prog.last_activity_at = datetime.now(timezone.utc)
        # compute score: count correct attempts
        from app.db.models import ExerciseAttempt
        attempts = (await db.execute(select(ExerciseAttempt).where(ExerciseAttempt.user_id == user.id, ExerciseAttempt.lesson_id == lesson_id))).scalars().all()
        correct = sum(1 for a in attempts if a.is_correct)
        total = len(attempts) if attempts else 1
        prog.score = int(100 * correct / total) if total else 100
        key = idempotency_key or f"lesson_complete:{user.id}:{lesson.id}"
        xp_awarded = await award_xp(db, user, lesson.xp_reward, "lesson_complete", source_id=str(lesson.id), idempotency_key=key)
        prog.xp_earned = (prog.xp_earned or 0) + xp_awarded
        user.profile.lessons_completed += 1
        user.profile.current_lesson_id = None
        # set next lesson
        next_lesson = (await db.execute(select(Lesson).where(Lesson.number == lesson.number + 1))).scalar_one_or_none()
        if next_lesson and can_access_lesson(user, next_lesson):
            user.profile.current_lesson_id = next_lesson.id
        await record_activity(db, user)
    await db.flush()
    return {"lesson_id": lesson.id, "xp_awarded": xp_awarded, "already_completed": already, "score": prog.score}

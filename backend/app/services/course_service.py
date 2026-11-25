from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.models import Course, Lesson, LessonProgress, User, UserProfile

async def list_courses(db: AsyncSession, user: User) -> list[Course]:
    result = await db.execute(select(Course).order_by(Course.order_index, Course.id))
    return list(result.scalars().all())

async def get_course(db: AsyncSession, course_id: int) -> Course | None:
    result = await db.execute(select(Course).where(Course.id == course_id))
    return result.scalar_one_or_none()

async def lessons_for_course(db: AsyncSession, user: User, course_id: int) -> list[Lesson]:
    result = await db.execute(select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.order_index, Lesson.number))
    lessons = list(result.scalars().all())
    # attach progress status
    progress_map = {}
    pres = await db.execute(select(LessonProgress).where(LessonProgress.user_id == user.id))
    for p in pres.scalars().all():
        progress_map[p.lesson_id] = p.status
    for l in lessons:
        l.status = progress_map.get(l.id, "not_started")  # type: ignore
    return lessons

async def get_lesson(db: AsyncSession, lesson_id: int) -> Lesson | None:
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    return result.scalar_one_or_none()

def can_access_lesson(user: User, lesson: Lesson) -> bool:
    if not lesson.is_premium:
        return True
    return bool(user.profile.is_premium)

async def get_lesson_progress(db: AsyncSession, user: User, lesson_id: int) -> LessonProgress | None:
    result = await db.execute(select(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson_id))
    return result.scalar_one_or_none()

async def start_lesson(db: AsyncSession, user: User, lesson_id: int) -> LessonProgress:
    prog = await get_lesson_progress(db, user, lesson_id)
    if not prog:
        prog = LessonProgress(user_id=user.id, lesson_id=lesson_id, status="in_progress", started_at=datetime_now(), last_activity_at=datetime_now())
        db.add(prog)
    else:
        prog.status = "in_progress"
        prog.last_activity_at = datetime_now()
    await db.flush()
    return prog

def datetime_now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models import Course, Lesson
from app.services.course_service import list_courses, get_course, lessons_for_course, get_lesson, can_access_lesson
from app.schemas.schemas import CourseOut, LessonOut

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut])
async def courses(db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    cs = await list_courses(db, user)
    out = []
    for c in cs:
        # count lessons
        from sqlalchemy import select, func
        total = (await db.execute(select(func.count(Lesson.id)).where(Lesson.course_id == c.id))).scalar() or 0
        completed = 0
        # completed count for user
        from app.db.models import LessonProgress
        comp = await db.execute(select(func.count(LessonProgress.id)).where(LessonProgress.user_id == user.id, LessonProgress.status == "completed").join(Lesson, Lesson.id == LessonProgress.lesson_id).where(Lesson.course_id == c.id))
        completed = comp.scalar() or 0
        co = CourseOut.model_validate(c)
        co.total_lessons = total
        co.completed_lessons = completed
        out.append(co)
    return out


@router.get("/{course_id}", response_model=CourseOut)
async def course_detail(course_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    c = await get_course(db, course_id)
    if not c:
        raise HTTPException(404, "Course not found")
    return c


@router.get("/{course_id}/lessons", response_model=list[LessonOut])
async def course_lessons(course_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    lessons = await lessons_for_course(db, user, course_id)
    out = []
    for l in lessons:
        lo = LessonOut.model_validate(l)
        lo.status = getattr(l, "status", "not_started")
        # access
        if l.is_premium and not user.profile.is_premium:
            lo.status = "locked"
        out.append(lo)
    return out

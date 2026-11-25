from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class TelegramUser(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    photo_url: Optional[str] = None


class AuthRequest(BaseModel):
    init_data: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


# ---------- User ----------
class UserOut(ORMModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    is_admin: bool = False
    created_at: datetime


class UserProfileOut(ORMModel):
    english_level: str
    total_xp: int
    level: int
    words_learned: int
    lessons_completed: int
    current_lesson_id: Optional[int] = None
    is_premium: bool
    premium_until: Optional[datetime] = None
    onboarding_completed: bool
    xp_to_next_level: int = 0


class UserSettingsOut(ORMModel):
    notifications_enabled: bool
    reminder_hour: int
    timezone: str
    theme: str


class UserSettingsUpdate(BaseModel):
    notifications_enabled: Optional[bool] = None
    reminder_hour: Optional[int] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None


class OnboardingRequest(BaseModel):
    english_level: str


# ---------- Hearts ----------
class HeartsOut(ORMModel):
    count: int
    max_count: int
    next_regen_at: Optional[datetime] = None
    seconds_to_next: Optional[int] = None


# ---------- XP ----------
class XPTransactionOut(ORMModel):
    id: int
    amount: int
    reason: str
    source_id: Optional[str] = None
    created_at: datetime


class XPAwardRequest(BaseModel):
    reason: str
    source_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    amount: Optional[int] = None


# ---------- Courses / Lessons ----------
class CourseOut(ORMModel):
    id: int
    slug: str
    title: str
    description: Optional[str] = None
    level: str
    is_premium: bool
    theme: Optional[str] = None
    order_index: int
    total_lessons: int = 0
    completed_lessons: int = 0


class LessonOut(ORMModel):
    id: int
    course_id: int
    number: int
    title: str
    description: Optional[str] = None
    level: str
    theme: Optional[str] = None
    is_premium: bool
    xp_reward: int
    status: Optional[str] = None


class ExerciseOut(ORMModel):
    id: int
    type: str
    question: str
    data: Dict[str, Any] = {}
    xp_reward: int
    order_index: int


class LessonDetail(ORMModel):
    lesson: LessonOut
    exercises: List[ExerciseOut] = []


class AnswerSubmit(BaseModel):
    exercise_id: int
    answer: str
    idempotency_key: Optional[str] = None


class AnswerResult(BaseModel):
    is_correct: bool
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    xp_awarded: int = 0
    hearts_remaining: Optional[int] = None
    lesson_completed: bool = False


class LessonCompleteRequest(BaseModel):
    lesson_id: int
    idempotency_key: Optional[str] = None


# ---------- Words / Cards ----------
class WordOut(ORMModel):
    id: int
    english: str
    russian: str
    transcription: Optional[str] = None
    example_en: Optional[str] = None
    example_ru: Optional[str] = None
    image_url: Optional[str] = None
    level: str
    theme: Optional[str] = None


class UserWordOut(ORMModel):
    id: int
    word: WordOut
    status: str
    next_review_at: Optional[datetime] = None
    times_correct: int
    times_wrong: int


class CardReviewRequest(BaseModel):
    word_id: int
    known: bool
    idempotency_key: Optional[str] = None


class VocabularyStats(BaseModel):
    total: int
    new: int
    learning: int
    known: int
    due_for_review: int


# ---------- Leagues ----------
class LeagueOut(ORMModel):
    id: int
    slug: str
    name: str
    tier: int


class LeagueParticipantOut(BaseModel):
    id: int
    name: str
    avatar: Optional[str] = None
    weekly_xp: int
    position: Optional[int] = None
    is_bot: bool
    is_user: bool = False


class LeagueStatus(BaseModel):
    league: LeagueOut
    season_end_at: datetime
    seconds_to_end: int
    user_position: Optional[int] = None
    user_weekly_xp: int = 0
    promotion_zone: int = 0
    demotion_zone: int = 0
    participants: List[LeagueParticipantOut] = []


# ---------- Premium ----------
class PremiumPlan(BaseModel):
    id: str
    title: str
    stars: int
    duration_days: int
    description: str
    best_value: bool = False


class CreateInvoiceRequest(BaseModel):
    plan: str


class CreateInvoiceResponse(BaseModel):
    invoice_link: str


class PremiumStatus(BaseModel):
    is_premium: bool
    premium_until: Optional[datetime] = None
    plan: Optional[str] = None


# ---------- Streak ----------
class StreakOut(ORMModel):
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[str] = None
    total_active_days: int


# ---------- Profile ----------
class ProfileOut(BaseModel):
    user: UserOut
    profile: UserProfileOut
    hearts: HeartsOut
    streak: StreakOut
    settings: UserSettingsOut


# ---------- Admin ----------
class AdminUserOut(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    english_level: Optional[str] = None
    total_xp: int = 0
    is_premium: bool = False
    created_at: datetime


class AdminStats(BaseModel):
    total_users: int
    premium_users: int
    total_lessons: int
    total_words: int
    total_payments: int


AuthResponse.model_rebuild()
ProfileOut.model_rebuild()
LessonDetail.model_rebuild()

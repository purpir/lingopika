from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    english: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    russian: Mapped[str] = mapped_column(String(256), nullable=False)
    transcription: Mapped[str | None] = mapped_column(String(128), nullable=True)
    example_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_ru: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    theme: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class UserWord(Base):
    __tablename__ = "user_words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), default="new", nullable=False)  # new/learning/known
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    times_correct: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    times_wrong: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="user_words")
    word: Mapped["Word"] = relationship("Word")

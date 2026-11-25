from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, JSON, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def now_utc():
    return datetime.now(timezone.utc)


class League(Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    tier: Mapped[int] = mapped_column(Integer, nullable=False)
    min_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    promotion_count: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    demotion_count: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    max_participants: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class LeagueSeason(Base):
    __tablename__ = "league_seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

    league: Mapped[League] = relationship("League")


class LeagueBot(Base):
    __tablename__ = "league_bots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    avatar: Mapped[str] = mapped_column(String(8), default="🤖", nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    base_xp_per_week: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    activity_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)


class LeagueParticipant(Base):
    __tablename__ = "league_participants"
    __table_args__ = (UniqueConstraint("season_id", "user_id", name="uq_season_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("league_seasons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    bot_id: Mapped[int | None] = mapped_column(ForeignKey("league_bots.id", ondelete="CASCADE"), nullable=True, index=True)
    weekly_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_bot: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False)

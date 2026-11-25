import asyncio
import os
import sys
import random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal, async_engine
from app.db.base import Base
from app.db.models import Course, Lesson, Exercise, Word
from app.content.data import LEVELS, THEME_WORDS, THEME_NAMES

FREE_LESSONS_PER_LEVEL = 800
PREMIUM_LESSONS_PER_THEME = 100
WORDS_PER_LESSON = 5
STUDY_CARDS_PER_LESSON = 4      # карточек изучения в начале урока
PRACTICE_EXERCISES_PER_LESSON = 6  # закрепляющих заданий
REVIEW_WORDS_PER_LESSON = 2     # 1-2 старых слова на урок для повторения


def make_study_card(word) -> dict:
    """Карточка изучения: просто показываем слово и перевод, без ввода."""
    return {
        "type": "study_card",
        "question": f"Изучи слово: {word[0]}",
        "data": {
            "word": {
                "english": word[0],
                "russian": word[1],
                "transcription": word[2],
                "example_en": word[3],
                "example_ru": word[4],
            }
        },
        "correct_answer": word[1],
        "explanation": f"{word[0]} — {word[1]}. {word[4]}",
        "xp_reward": 1,
    }


def make_exercises(lesson_id: int, words: list, level: str, review_words: list = None) -> list[dict]:
    exs = []

    # --- ФАЗА ИЗУЧЕНИЯ: study_card ---
    for w in words[:STUDY_CARDS_PER_LESSON]:
        exs.append(make_study_card(w))

    # --- ФАЗА ЗАКРЕПЛЕНИЯ: обычные задания ---
    practice_words = list(words)
    if review_words:
        # добавляем старые слова для повторения (случайно 1-2 шт)
        practice_words.extend(random.sample(review_words, min(2, len(review_words))))
        random.shuffle(practice_words)

    # multiple_choice для первых 2 слов
    for w in practice_words[:2]:
        distractors = [x[1] for x in words if x[0] != w[0]][:3]
        options = [w[1]] + distractors
        while len(options) < 4:
            options.append("—")
        exs.append({
            "type": "multiple_choice",
            "question": f"Перевод: {w[0]}",
            "data": {"options": options[:4]},
            "correct_answer": w[1],
            "explanation": f"{w[0]} = {w[1]}",
            "xp_reward": 5,
        })

    # translate_en_ru для 1 слова
    for w in practice_words[2:3]:
        exs.append({
            "type": "translate_en_ru",
            "question": w[0],
            "data": {},
            "correct_answer": w[1],
            "explanation": w[4],
            "xp_reward": 5,
        })

    # translate_ru_en для 1 слова
    for w in practice_words[3:4]:
        exs.append({
            "type": "translate_ru_en",
            "question": w[1],
            "data": {},
            "correct_answer": w[0],
            "explanation": w[3],
            "xp_reward": 5,
        })

    # arrange для 1 слова — переведи предложение (случайно EN→RU или RU→EN)
    for w in practice_words[4:5]:
        example_en = w[3]
        example_ru = w[4]
        if random.random() < 0.5:
            source = example_en
            target = example_ru
        else:
            source = example_ru
            target = example_en
        tokens = target.strip(".").split()
        shuffled = list(tokens)
        random.shuffle(shuffled)
        exs.append({
            "type": "arrange",
            "question": f"Переведи предложение: {source}",
            "data": {"tokens": shuffled, "answer_tokens": tokens},
            "correct_answer": target,
            "explanation": f"{example_en} — {example_ru}",
            "xp_reward": 5,
        })

    # fill_blank для 1 слова
    for w in practice_words[:1]:
        exs.append({
            "type": "fill_blank",
            "question": f"Вставь пропуск: I like ___ ({w[1]})",
            "data": {"sentence": "I like ___ .", "hint": w[1]},
            "correct_answer": w[0],
            "explanation": f"I like {w[0]}.",
            "xp_reward": 5,
        })

    return exs


def chunk_words(words, i):
    n = len(words)
    start = (i * WORDS_PER_LESSON) % n
    chunk = []
    for j in range(WORDS_PER_LESSON):
        chunk.append(words[(start + j) % n])
    return chunk


async def seed():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        lesson_number = 1
        all_seen_words = []  # все слова, которые уже встречались (для повторений)

        # free main courses
        for level, words in LEVELS.items():
            course = Course(
                slug=f"course-{level.lower()}",
                title=f"English {level}",
                description=f"Course for level {level}",
                level=level,
                is_premium=False,
                order_index=0,
            )
            db.add(course)
            await db.flush()

            for i in range(FREE_LESSONS_PER_LEVEL):
                chunk = chunk_words(words, i)

                # выбираем 1-2 слова для повторения из уже проученных (каждый урок)
                review_words = []
                if all_seen_words:
                    review_words = random.sample(all_seen_words, min(REVIEW_WORDS_PER_LESSON, len(all_seen_words)))

                exs = make_exercises(lesson_number, chunk, level, review_words)

                lesson = Lesson(
                    course_id=course.id,
                    number=lesson_number,
                    title=f"Lesson {lesson_number}: {chunk[0][0].capitalize()}",
                    description=f"Learn words: {', '.join(w[0] for w in chunk)}",
                    level=level,
                    is_premium=False,
                    xp_reward=20,
                    content={
                        "words": [
                            {
                                "english": w[0],
                                "russian": w[1],
                                "transcription": w[2],
                                "example_en": w[3],
                                "example_ru": w[4],
                            }
                            for w in chunk
                        ]
                    },
                )
                db.add(lesson)
                await db.flush()

                for w in chunk:
                    db.add(
                        Word(
                            english=w[0],
                            russian=w[1],
                            transcription=w[2],
                            example_en=w[3],
                            example_ru=w[4],
                            level=level,
                            lesson_id=lesson.id,
                        )
                    )
                    await db.flush()

                all_seen_words.extend(chunk)

                for idx, e in enumerate(exs):
                    db.add(
                        Exercise(
                            lesson_id=lesson.id,
                            type=e["type"],
                            question=e["question"],
                            data=e["data"],
                            correct_answer=e["correct_answer"],
                            explanation=e["explanation"],
                            xp_reward=e["xp_reward"],
                            order_index=idx,
                        )
                    )
                lesson_number += 1
            await db.flush()

        # premium thematic courses
        for theme, words in THEME_WORDS.items():
            course = Course(
                slug=f"theme-{theme}",
                title=THEME_NAMES.get(theme, theme),
                description=f"Thematic course: {theme}",
                level="B1",
                is_premium=True,
                theme=theme,
                order_index=100,
            )
            db.add(course)
            await db.flush()

            for i in range(PREMIUM_LESSONS_PER_THEME):
                chunk = chunk_words(words, i)

                review_words = []
                if all_seen_words:
                    review_words = random.sample(all_seen_words, min(REVIEW_WORDS_PER_LESSON, len(all_seen_words)))

                exs = make_exercises(lesson_number, chunk, "B1", review_words)

                lesson = Lesson(
                    course_id=course.id,
                    number=lesson_number,
                    title=f"Thematic: {chunk[0][0].capitalize()}",
                    description=f"Theme {theme}: {', '.join(w[0] for w in chunk)}",
                    level="B1",
                    theme=theme,
                    is_premium=True,
                    xp_reward=25,
                    content={
                        "words": [
                            {
                                "english": w[0],
                                "russian": w[1],
                                "transcription": w[2],
                                "example_en": w[3],
                                "example_ru": w[4],
                            }
                            for w in chunk
                        ]
                    },
                )
                db.add(lesson)
                await db.flush()

                for w in chunk:
                    db.add(
                        Word(
                            english=w[0],
                            russian=w[1],
                            transcription=w[2],
                            example_en=w[3],
                            example_ru=w[4],
                            level="B1",
                            theme=theme,
                            lesson_id=lesson.id,
                        )
                    )
                    await db.flush()

                all_seen_words.extend(chunk)

                for idx, e in enumerate(exs):
                    db.add(
                        Exercise(
                            lesson_id=lesson.id,
                            type=e["type"],
                            question=e["question"],
                            data=e["data"],
                            correct_answer=e["correct_answer"],
                            explanation=e["explanation"],
                            xp_reward=e["xp_reward"],
                            order_index=idx,
                        )
                    )
                lesson_number += 1
            await db.flush()

        await db.commit()
        print(f"Seeded up to lesson {lesson_number - 1}")


if __name__ == "__main__":
    asyncio.run(seed())

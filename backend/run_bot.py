import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

from app.config import settings

logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else None
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Open LingoPika", web_app=types.WebAppInfo(url=settings.TELEGRAM_WEBHOOK_URL or "http://localhost:5173"))]
    ])
    await message.answer("Welcome to LingoPika! 🐹", reply_markup=kb)


@dp.pre_checkout_query()
async def pre_checkout(query: types.PreCheckoutQuery):
    await query.answer(ok=True)


@dp.message(F.successful_payment)
async def successful_payment(message: types.Message):
    payment = message.successful_payment
    # process in DB
    from app.db.session import AsyncSessionLocal
    from app.services.premium_service import activate_premium
    from app.services.user_service import get_user_by_telegram_id
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            return
        # parse plan from payload
        payload = payment.invoice_payload
        plan = "weekly"
        if "monthly" in payload:
            plan = "monthly"
        await activate_premium(db, user, plan, payment.telegram_payment_charge_id, payment.provider_payment_charge_id, payment.model_dump() if hasattr(payment, "model_dump") else None)
        await db.commit()
    await message.answer("Premium activated! 🎉")


async def main():
    if not bot:
        print("No bot token configured")
        return
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

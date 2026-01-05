import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

from bots.config import BOT_TOKEN, ADMIN_IDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Простая клавиатура
def get_main_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🛒 Купить подписку", callback_data="buy")],
        [InlineKeyboardButton(text="📊 Моя подписка", callback_data="status")],
        [InlineKeyboardButton(text="⚙️ Помощь", callback_data="help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🚀 Добро пожаловать в VPN сервис!\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )

@dp.callback_query(lambda c: c.data == "buy")
async def buy_subscription(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Выберите тариф:\n"
        "• Премиум - $9.99/месяц\n"
        "• Стандарт - $4.99/месяц\n\n"
        "Напишите /premium или /standard",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
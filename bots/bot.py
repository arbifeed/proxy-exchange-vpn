import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN, BACKEND_URL

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(commands=["start"])
async def start(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BACKEND_URL}/v1/auth/tg_register", params={"tg_id": message.from_user.id}
        ) as resp:
            data = await resp.json()

    api_key = data["api_key"]
    await message.answer(f"Ваш API-key: {api_key}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

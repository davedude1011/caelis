import asyncio

from aiogram import Dispatcher, Router, types
from aiogram.filters import CommandStart

from bot.bot_instance import bot
from bot.handlers.global_handlers import register_routers

dp = Dispatcher()

async def main() -> None:
    register_routers(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

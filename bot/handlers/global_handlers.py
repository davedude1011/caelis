from bot.handlers.anime import anime_router
from bot.handlers.img import img_router
from bot.handlers.cil import cil_router

from aiogram import Dispatcher

def register_routers(dp: Dispatcher) -> None:
    dp.include_routers(
        anime_router,
        img_router,
        cil_router,
    )
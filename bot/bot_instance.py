from aiogram import Bot, types

from dotenv import load_dotenv
from os import getenv

load_dotenv()
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(
    token=TELEGRAM_BOT_TOKEN,
)
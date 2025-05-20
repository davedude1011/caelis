from aiogram import Router, F
from aiogram.types import Message

from bot.bot_instance import bot

from bot.handlers.handler_tools import Command, global_tags, FunctionGroupSchema, TagSchema, TagParameterSchema, parse_tags
from data.user import CaelisUser

from google import genai

from dotenv import load_dotenv
from os import getenv

load_dotenv()
GEMINI_API_KEY = getenv("GEMINI_API_KEY")

cil_router = Router()

@cil_router.message(Command("cil"))
async def cil_handler(message: Message):
    client = genai.Client(api_key=GEMINI_API_KEY)

    response = client.models.generate_content(
        model="gemini-1.5-flash", contents=message.text
    )
    
    await message.answer(response.text)
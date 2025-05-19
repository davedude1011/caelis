from aiogram import Router, F
from aiogram.types import Message

from bot.bot_instance import bot

from bot.handlers.handler_tools import Command, global_tags, FunctionGroupSchema, TagSchema, TagParameterSchema, parse_tags
from data.user import CaelisUser

from data.animedata.animedata import GLOBAL_ANIME_SHOWS

anime_router = Router()

global_tags.add_function_group(FunctionGroupSchema(
    title="ani",
    tag_list=[
        TagSchema(["h","help"], []),

        TagSchema(["ls","list_shows"], [
            TagParameterSchema(True, "str", "search"),
        ]),
        TagSchema(["le","list_episodes"], [
            TagParameterSchema(False, "int", "show id"),
        ]),

        TagSchema(["ss","send_shows", "ps", "play_shows"], [
            TagParameterSchema(False, "str", "comma separated list of show id's"),
            TagParameterSchema(True, "str", "comma separated list of episode numbers"),
        ]),
        TagSchema(["se","send_episodes", "pe", "play_episodes"], [
            TagParameterSchema(False, "str", "comma separated list of episode id's"),
        ]),
    ],
))

@anime_router.message(Command("ani"))
async def anime_handler(message: Message) -> None:
    parsed_command = parse_tags(message.text)
    tags = parsed_command.tags

    if len(tags) == 0:
        await message.answer("Please provide some tags! Try 'ani -help' for more info on tags!")
        return

    for tag in tags:
        user_data = CaelisUser(message.from_user)

        if tag.key in ["h", "help"]:
            await message.answer(global_tags.get_group("ani").generate_help_text())

        elif tag.key in ["ls", "list-shows"]:
            await list_shows(message, tag.params[0])

        elif tag.key in ["le", "list-episodes"]:
            await list_episodes(message, tag.params[0])

        elif tag.key in ["ss", "send-shows", "ps", "play_shows"]:
            await send_shows(message, tag.params[0], tag.params[1])

        elif tag.key in ["se", "send-episodes", "pe", "play_episodes"]:
            await send_episodes(message, tag.params[0])


async def list_shows(message: Message, search: str | None) -> None:
    await message.answer(GLOBAL_ANIME_SHOWS.list_shows(search))

async def list_episodes(message: Message, show_id: int | None) -> None:
    if not show_id:
        await message.answer("Please provide a show id, if you do not know the show id then find the show using 'ani -ls' and the show id will be on the left of each title!")
        return

    show = GLOBAL_ANIME_SHOWS.get_show(show_id)

    if not show:
        await message.answer("This show id does not match any known shows :-(")
        return

    await message.answer(show.list_episodes())

async def send_shows(message: Message, show_ids: str, episode_nums: str) -> None:
    if not show_ids:
        await message.answer("You must provide the list or singular show id!")

    try:
        ids = [int(_) for _ in show_ids.split(",")]
    except:
        await message.answer("Must be a comma separated list of (integer) ids of shows!")
        return
    
    for show_id in ids:
        show = GLOBAL_ANIME_SHOWS.get_show(show_id)

        if not show:
            continue
            
        await send_episodes(message, ",".join([str(_.id) for _ in show.episodes if not episode_nums or _.episode in [int(__) for __ in episode_nums.split(",")]]))

async def send_episodes(message: Message, episode_ids: str | None) -> None:
    if not episode_ids:
        await message.answer("You must provide the list or singular episode id!")

    try:
        ids = [int(_) for _ in episode_ids.split(",")]
    except:
        await message.answer("Must be a comma separated list of (integer) ids of episodes!")
        return

    for episode_id in ids:
        fairu_id = -1002581642121

        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=fairu_id,
            message_id=episode_id,
        )
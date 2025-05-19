from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile, CallbackQuery, InputMediaPhoto

from bot.bot_instance import bot

from bot.handlers.handler_tools import Command, global_tags, FunctionGroupSchema, TagSchema, TagParameterSchema, parse_tags
from data.user import CaelisUser

import uuid

img_router = Router()

global_tags.add_function_group(FunctionGroupSchema(
    title="img",
    tag_list=[
        TagSchema(["h","help"], []),

        TagSchema(["lc","list-collections"], [
            TagParameterSchema(True, "str", "search parameter"),
        ]),
        TagSchema(["tc","toggle-collections"], [
            TagParameterSchema(False, "str", "collection name"),
        ]),
        TagSchema(["cc","create-collection"], [
            TagParameterSchema(False, "str", "collection name"),
        ]),
        TagSchema(["dc","delete-collection"], [
            TagParameterSchema(False, "str", "collection name"),
        ]),

        TagSchema(["li","list-images"], [
            TagParameterSchema(False, "str", "collection name"),
            TagParameterSchema(True, "int", "from index"),
            TagParameterSchema(True, "int", "to index"),
        ]),

        TagSchema(["gi", "generate-image"], [
            TagParameterSchema(False, "str", "prompt"),
            TagParameterSchema(True, "str", "negative prompt"),
            TagParameterSchema(True, "int", "width"),
            TagParameterSchema(True, "int", "height"),
        ]),
    ],
))

@img_router.message(Command("img"))
async def img_handler(message: Message) -> None:
    parsed_command = parse_tags(message.text)
    tags = parsed_command.tags

    if len(tags) == 0:
        await message.answer("Please provide some tags! Try 'img -help' for more info on tags!")
        return

    for tag in tags:
        user_data = CaelisUser(message.from_user)

        if tag.key in ["h", "help"]:
            await message.answer(global_tags.get_group("img").generate_help_text())

        elif tag.key in ["lc", "list-collections"]:
            await list_collections(message, user_data, tag.params[0])

        elif tag.key in ["tc", "toggle-collection"]:
            await toggle_collection(message, user_data, tag.params[0])
        
        elif tag.key in ["cc", "create-collection"]:
            await create_collection(message, user_data, tag.params[0])

        elif tag.key in ["dc", "delete-collection"]:
            await delete_collection(message, user_data, tag.params[0])

        elif tag.key in ["li", "list-images"]:
            await list_images(message, user_data, tag.params[0], tag.params[1], tag.params[2])
        
        elif tag.key in ["gi", "generate-images"]:
            await generate_image(message, user_data, tag.params[0], tag.params[1], tag.params[2], tag.params[3])

# ===== Collections =====

@img_router.message(lambda message: message.photo)
async def collection_input_handler(message: Message) -> None:
    user_data = CaelisUser(message.from_user)

    active_collections = [collection for collection in user_data.image_collections.get_all_collections() if collection.active_multiselect]

    if len(active_collections) == 0:
        return
    
    image = message.photo[-1]
    
    file = await bot.get_file(image.file_id)

    await bot.download_file(
        file_path=file.file_path,
        destination=f"images/{image.file_unique_id}.jpg",
    )

    for collection in active_collections:
        collection.create_image(
            width=image.width,
            height=image.height,
            filesize=image.file_size,
            fileid=image.file_unique_id,
        )
    
    await message.answer(f"Added image to these collections: {', '.join([collection.title for collection in active_collections])}")


async def list_collections(message: Message, user_data: CaelisUser, search: str | None = None) -> None:
    user_collections = user_data.image_collections.get_all_collections()

    if search:
        user_collections = [collection for collection in user_collections if search.lower() in collection.title.lower()]
    
    response = f"You have {len(user_collections)} {'collections' if len(user_collections) != 1 else 'collection'}:"

    for collection in user_collections:
        response += f"\n<b>• {collection.title}</b> ({len(collection.get_images())}) {'(selected)' if collection.active_multiselect else ''}"

    await message.answer(response)

async def toggle_collection(message: Message, user_data: CaelisUser, collection_title: str | bool) -> None:
    if collection_title == True:
        await message.answer(f"Please provide the name of the collection!")
        return

    collection = user_data.image_collections.get_collection(collection_title)

    if not collection:
        await message.answer(f"You do not have an collection named {collection_title}!")
        return

    if collection.active_multiselect:
        await message.answer(f"selection disabled for {collection_title}")
        collection.set_active_multiselect(False)
    
    else:
        await message.answer(f"selection enabled for {collection_title}")
        collection.set_active_multiselect(True)

async def create_collection(message: Message, user_data: CaelisUser, collection_title: str | bool) -> None:
    if collection_title == True:
        await message.answer("Please provide the name of the new collection!")
        return
    
    existing_user_collection_titles = [collection.title for collection in user_data.image_collections.get_all_collections()]
    
    if collection_title in existing_user_collection_titles:
        await message.answer(f"You already have a collection named {collection_title}!")
        return
    
    user_data.image_collections.create_collection(collection_title)
    await message.answer(f"Successfully created collection {collection_title}!")

async def delete_collection(message: Message, user_data: CaelisUser, collection_title: str | bool) -> None:
    if collection_title == True:
        await message.answer("Please provide the name of the collection to delete!")
        return
    
    collection = user_data.image_collections.get_collection(collection_title)

    if not collection:
        await message.answer(f"You do not have a collection named {collection_title}!")
        return

    collection.suicide()

    await message.answer(f"Successfully deleted collection {collection_title}!")


collection_navigation_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(
        text="Previous",
        callback_data="collection_image_prev",
    ),
    InlineKeyboardButton(
        text="Next",
        callback_data="collection_image_next",
    ),
]])

async def list_images(message: Message, user_data: CaelisUser, collection_title: str | bool, from_index: int | None, to_index: int | None) -> None:
    if collection_title == True:
        await message.answer(f"Please provide the name of the collection!")
        return

    collection = user_data.image_collections.get_collection(collection_title)

    if not collection:
        await message.answer(f"You do not have an collection named {collection_title}!")
        return

    images = collection.get_images()

    if from_index and from_index > len(images):
        await message.answer(f"{collection_title} does not contain {from_index} images!")
        return
    
    if to_index and to_index > len(images):
        await message.answer(f"{collection_title} does not contain {to_index} images!")
        return
    
    images = images[from_index - 1 if from_index else 0 : to_index if to_index else len(images)]

    with open(f"images/{images[0].fileid}.jpg", "rb") as photo_file:
        photo = BufferedInputFile(photo_file.read(), filename=images[0].fileid)
    
    passed_index_addon = f"| <i>{from_index if from_index else 1} - {to_index if to_index else len(images)}</i>" if from_index or to_index else ""

    await message.answer_photo(
        photo=photo,
        caption=f"1/{len(images)} | <code>{collection.title}</code> {passed_index_addon}",
        reply_markup=collection_navigation_keyboard_markup,
    )

@img_router.callback_query(F.data.in_({"collection_image_prev", "collection_image_next"}))
async def collection_navigation_handler(callback: CallbackQuery):
    caption =  callback.message.caption
    image_index = int(caption.split("/")[0]) - 1

    collection_title = caption.split("|")[1].strip()

    from_index, to_index = None, None
    if len(caption.split("|")) > 2:
        from_index, to_index = [int(index.strip()) for index in caption.split("|")[2].strip().split("-")]

    user_data = CaelisUser(callback.from_user)
    
    collection = user_data.image_collections.get_collection(collection_title)

    if not collection:
        await callback.answer(f"Image collection not found, title={collection_title}!")
        return

    images = collection.get_images()
    
    images = images[from_index - 1 if from_index else 0 : to_index if to_index else len(images)]

    if len(images) < 2:
        await callback.answer("Only one image?")
        return

    if callback.data == "collection_image_prev":
        if image_index == 0:
            image_index = len(images)-1
        else:
            image_index -= 1
    elif callback.data == "collection_image_next":
        if image_index == len(images)-1:
            image_index = 0
        else:
            image_index += 1
    
    image = images[image_index]

    if not image:
        await callback.answer(f"Image of index {image_index} not found in collection {collection_title}!")
        return

    with open(f"images/{image.fileid}.jpg", "rb") as photo_file:
        photo = BufferedInputFile(photo_file.read(), filename=image.fileid)
    
    passed_index_addon = f"| <i>{from_index if from_index else 1} - {to_index if to_index else len(images)}</i>" if from_index or to_index else ""

    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=f"{image_index+1}/{len(images)} | <code>{collection_title}</code> {passed_index_addon}",
        ),
        reply_markup=collection_navigation_keyboard_markup,
    )

# ===== Pollinations =====

import aiohttp
import random
import urllib.parse
import os

async def generate_image(message: Message, user_data: CaelisUser, prompt: str, negative: str | None, width: int | None, height: int | None) -> None:
    if not prompt:
        await message.answer("Please provide the prompt!")
        return

    # Construct the API URL
    base_url = "https://image.pollinations.ai/prompt/"
    encoded_prompt = urllib.parse.quote(prompt)
    params = {
        "width": width if width else 1024,
        "height": height if height else 1024,
        "nologo": "true",
        "seed": random.randint(0, 999999),
    }
    if negative:
        params["negative"] = negative

    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}{encoded_prompt}?{query_string}"

    filename = f"{user_data.user.id}.{uuid.uuid4().hex}"
    path = f"images/{filename}.jpg"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await message.answer(
                    text="Failed to generate image.",
                    reply_to_message_id=message.message_id,
                )
                return
            image_bytes = await response.read()
            with open(path, "wb") as f:
                f.write(image_bytes)

    with open(path, "rb") as photo_file:
        photo = BufferedInputFile(photo_file.read(), filename=filename)

    await message.answer_photo(
        photo=photo,
        reply_to_message_id=message.message_id
    )

    active_collections = [collection for collection in user_data.image_collections.get_all_collections() if collection.active_multiselect]

    if len(active_collections) == 0:
        return

    for collection in active_collections:
        collection.create_image(
            width=width if width else 1024,
            height=height if height else 1024,
            filesize=os.path.getsize(path),
            fileid=filename,
        )
    
    await message.answer(f"Added generated image to these collections: {', '.join([collection.title for collection in active_collections])}")
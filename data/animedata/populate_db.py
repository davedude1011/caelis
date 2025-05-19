import asyncio
import re
import sqlite3
from dotenv import load_dotenv
from os import getenv
from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, DocumentAttributeVideo

# Load environment variables
load_dotenv()
TELEGRAM_API_ID = getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = getenv("TELEGRAM_API_HASH")
target_chat = 'https://t.me/+YtcMOPxvxFI4YzA0'

client = TelegramClient('session_name', TELEGRAM_API_ID, TELEGRAM_API_HASH)

DB_PATH = "data/animedata/animedata.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear and reset tables
cursor.execute("DELETE FROM episodes;")
cursor.execute("DELETE FROM shows;")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='episodes';")
cursor.execute("DELETE FROM sqlite_sequence WHERE name='shows';")
conn.commit()

def parse_caption(caption: str):
    match = re.search(r'(.+?) - S(\d{2,3})E(\d{2,3}) - (.+)', caption)
    if not match:
        return None
    return {
        "show_title": match.group(1).strip(),
        "season": int(match.group(2)),
        "episode": int(match.group(3)),
        "episode_title": match.group(4).strip()
    }

async def main():
    await client.start()
    print(f"Fetching messages from {target_chat}...")

    # Step 1: Collect all episodes first (oldest first)
    episodes = []
    async for message in client.iter_messages(target_chat, reverse=True):  # reverse=True = oldest first
        if (
            message.media
            and isinstance(message.media, MessageMediaDocument)
            and any(isinstance(attr, DocumentAttributeVideo) for attr in message.media.document.attributes)
        ):
            caption = message.message or ""
            data = parse_caption(caption)
            if not data:
                continue
            episodes.append({
                "message_id": message.id,
                "show_title": data["show_title"],
                "season": data["season"],
                "episode": data["episode"],
                "episode_title": data["episode_title"],
            })

    print(f"Collected {len(episodes)} episodes.")

    # Step 2: Extract unique shows and insert sorted alphabetically
    unique_shows = sorted(set(ep["show_title"] for ep in episodes))
    show_title_to_id = {}

    for show_title in unique_shows:
        cursor.execute("INSERT INTO shows (title) VALUES (?);", (show_title,))
        show_title_to_id[show_title] = cursor.lastrowid

    conn.commit()

    # Step 3: Insert episodes in the order collected (oldest first, i.e. reversed from normal)
    for ep in episodes:
        show_id = show_title_to_id[ep["show_title"]]
        cursor.execute(
            "INSERT INTO episodes (id, show_id, title, episode, season) VALUES (?, ?, ?, ?, ?);",
            (
                ep["message_id"],
                show_id,
                ep["episode_title"],
                ep["episode"],
                ep["season"],
            )
        )

    conn.commit()
    print("Done inserting all episodes.")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

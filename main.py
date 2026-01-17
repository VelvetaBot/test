import os, asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("velveta", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_links = {}
user_quality = {}

WELCOME = """🌟 Welcome to Velveta Downloader (Pro)! 🌟  
I can download videos up to 2GB! 🚀  

How to use:  
1️⃣ Send a YouTube link 🔗  
2️⃣ Select Quality ✨  
3️⃣ Wait for the magic! 📥  
"""

# /start
@app.on_message(filters.command("start"))
async def start(client, msg):
    kb = [[InlineKeyboardButton("Join update channel", url="https://t.me/Velvetabots")]]
    await msg.reply(WELCOME, reply_markup=InlineKeyboardMarkup(kb))

# Get YouTube Link
@app.on_message(filters.text & ~filters.command)
async def get_link(client, msg):
    link = msg.text.strip()
    if "youtube" not in link and "youtu.be" not in link:
        await msg.reply("❌ Send only YouTube link")
        return

    user_links[msg.from_user.id] = link
    kb = [
        [InlineKeyboardButton("360p", callback_data="q360"),
         InlineKeyboardButton("480p", callback_data="q480")],
        [InlineKeyboardButton("720p", callback_data="q720"),
         InlineKeyboardButton("MP3", callback_data="qmp3")]
    ]
    await msg.reply("Select Quality:", reply_markup=InlineKeyboardMarkup(kb))

# Quality select
@app.on_callback_query(filters.regex("^q"))
async def choose_quality(client, cb):
    uid = cb.from_user.id
    user_quality[uid] = cb.data
    link = user_links.get(uid)

    await cb.message.edit("⬇️ Downloading...\n[□□□□□□] 0%")
    asyncio.create_task(download_video(cb.message, uid, link))

# Progress bar
async def progress(d, message):
    if d["status"] == "downloading":
        p = d["_percent_str"].replace("%","")
        try:
            val = float(p)
        except:
            return
        bar = int(val // 10)
        text = "⬇️ Downloading...\n[" + "■"*bar + "□"*(10-bar) + f"] {val:.0f}%"
        try:
            await message.edit(text)
        except:
            pass

# Auto-switch server download
async def download_video(message, uid, link):
    q = user_quality[uid]
    if q == "q360": fmt = "bestvideo[height<=360]+bestaudio/best"
    elif q == "q480": fmt = "bestvideo[height<=480]+bestaudio/best"
    elif q == "q720": fmt = "bestvideo[height<=720]+bestaudio/best"
    else: fmt = "bestaudio"

    servers = [
        {},
        {"retries": 5},
        {"socket_timeout": 30},
        {"force_ipv4": True},
        {"source_address": "0.0.0.0"}
    ]

    for server in servers:
        ydl_opts = {
            "format": fmt,
            "outtmpl": f"{uid}.%(ext)s",
            "progress_hooks": [lambda d: asyncio.create_task(progress(d, message))],
            **server
        }
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

            file = next(f for f in os.listdir() if f.startswith(str(uid)))
            await message.reply_video(file)
            os.remove(file)

            kb = [
                [InlineKeyboardButton("❤️ Donate", url="https://buymeacoffee.com/VelvetaBots")],
                [InlineKeyboardButton("🔁 Replay", callback_data="replay")]
            ]
            await message.reply("✅ Download Complete!", reply_markup=InlineKeyboardMarkup(kb))
            return
        except:
            continue

    await message.edit("❌ Download failed. Try another link.")

# Replay
@app.on_callback_query(filters.regex("replay"))
async def replay(client, cb):
    uid = cb.from_user.id
    link = user_links.get(uid)
    if link:
        fake_msg = cb.message
        fake_msg.text = link
        await get_link(client, fake_msg)

app.run()

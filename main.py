import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL

# --- မင်းပေးထားတဲ့ အချက်အလက်တွေ (အပြည့်အစုံထည့်ပြီး) ---
API_ID = 32642557
API_HASH = "2790877135ea0991a392fe6a0d285c27"
BOT_TOKEN = "8459123928:AAFREMWam1sdTZCgS5ieHnJ3N0pz1smbvmo"
ADMIN_ID = 6363229693  # သားကြီးရဲ့ ID

app = Client("my_pro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}
db_file = "users.txt"

# User စာရင်းမှတ်တမ်းသွင်းခြင်း
def add_user(user_id):
    if not os.path.exists(db_file): open(db_file, "w").close()
    with open(db_file, "r+") as f:
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    add_user(message.from_user.id)
    await message.reply_text(
        f"👋 **မင်္ဂလာပါ {message.from_user.first_name}!**\n\n"
        "ကျွန်တော်က YouTube ကနေ သီချင်းတွေကို Cover Photo နဲ့တကွ Quality ကောင်းကောင်း ဒေါင်းပေးမယ့် Bot ပါ။\n\n"
        "🔍 **သီချင်းနာမည်** သို့မဟုတ် **Link** တစ်ခုခု ပို့ပေးလိုက်ပါ သားကြီး!"
    )

@app.on_message(filters.command("stats") & filters.user(ADMIN_ID))
async def stats(client, message):
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            count = len(f.read().splitlines())
        await message.reply_text(f"📊 **Admin Panel**\n\nလက်ရှိအသုံးပြုသူစုစုပေါင်း: {count} ယောက်")
    else:
        await message.reply_text("အသုံးပြုသူ မရှိသေးပါ!")

@app.on_message(filters.text & filters.private)
async def handle_input(client, message):
    if message.text.startswith("/"): return
    user_id = message.from_user.id
    user_data[user_id] = message.text
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔈 128kbps", callback_data="128"),
         InlineKeyboardButton("📻 192kbps", callback_data="192")],
        [InlineKeyboardButton("🎧 320kbps (Pro)", callback_data="320")]
    ])
    await message.reply_text("💿 ဘယ်လို Quality မျိုးနဲ့ ဒေါင်းမလဲ သားကြီး?", reply_markup=buttons)

@app.on_callback_query()
async def download_logic(client, callback_query):
    user_id = callback_query.from_user.id
    quality = callback_query.data
    query = user_data.get(user_id)

    if not query: return

    msg = await callback_query.message.edit_text("⏳ YouTube မှာ ရှာဖွေနေပါတယ်... ခဏစောင့်ပေးပါ...")

    if not os.path.exists("downloads"): os.makedirs("downloads")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': quality},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ],
        'ffmpeg_location': './ffmpeg.exe',
        'nocheckcertificate': True,
        'quiet': True,
        'writethumbnail': True,
    }

    try:
        search_query = query if "youtube.com" in query or "youtu.be" in query else f"ytsearch1:{query}"
        
        with YoutubeDL(ydl_opts) as ydl:
            await msg.edit_text(f"📥 **Quality {quality}kbps** နဲ့ ဒေါင်းလုဒ်ဆွဲနေပါပြီ...")
            info = await asyncio.to_thread(ydl.extract_info, search_query, download=True)
            video_info = info['entries'][0] if 'entries' in info else info
            file_path = ydl.prepare_filename(video_info).replace(video_info['ext'], 'mp3')
            title = video_info.get('title', 'Unknown Title')
            performer = video_info.get('uploader', 'Music Bot')

        await msg.edit_text("📤 Telegram ပေါ် တင်ပေးနေပါပြီ... ခဏလေးနော်...")
        
        await client.send_audio(
            chat_id=user_id,
            audio=file_path,
            title=title,
            performer=performer,
            caption=f"🎵 **{title}**\n🔥 Quality: {quality}kbps\n\n✅ @my_audio_dl_bot"
        )
        await msg.delete()
        
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

print("🚀 Bot ကို အောင်မြင်စွာ စတင်လိုက်ပါပြီ သားကြီး!")
app.run()
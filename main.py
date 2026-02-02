import os
import telebot
import yt_dlp
from telebot import types

# BotFather ကပေးတဲ့ Token အသစ်
API_TOKEN = '8459123928:AAGBy-sjsNb5Z8hjU3ahJqzcc-iiX0bIjaI'
bot = telebot.TeleBot(API_TOKEN)

# User ရဲ့ ရှာဖွေမှုတွေကို မှတ်ထားဖို့
user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "နေကောင်းလား သားကြီး! သီချင်းနာမည် ဒါမှမဟုတ် YouTube Link ပို့ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    chat_id = message.chat.id
    user_data[chat_id] = query

    # Quality ရွေးဖို့ Button များ
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("🔈 128kbps", callback_data="128")
    item2 = types.InlineKeyboardButton("📻 192kbps", callback_data="192")
    item3 = types.InlineKeyboardButton("🎧 320kbps (Pro)", callback_data="320")
    markup.add(item1, item2)
    markup.add(item3)

    bot.send_message(chat_id, "📀 ဘယ်လို Quality မျိုးနဲ့ ဒေါင်းမလဲ သားကြီး?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    quality = call.data
    query = user_data.get(chat_id)

    if not query:
        bot.send_message(chat_id, "❌ အချက်အလက် ပြန်ရိုက်ပေးပါဦး။")
        return

    sent_msg = bot.send_message(chat_id, f"📥 {quality}kbps နဲ့ ရှာဖွေဒေါင်းလုဒ်လုပ်နေတယ်...")

    # yt-dlp options (NoneType error နဲ့ FFmpeg error ကာကွယ်ရန်)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt', 
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False, # NoneType error အတွက် အရေးကြီးသည်
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube မှာ ရှာဖွေခြင်း (ytsearch1: သုံးထားသည်)
            search_query = f"ytsearch1:{query}" if not query.startswith('http') else query
            info = ydl.extract_info(search_query, download=True)
            
            if info is None:
                raise Exception("သီချင်းရှာမတွေ့ပါ")

            if 'entries' in info:
                info = info['entries'][0]
            
            filename = ydl.prepare_filename(info)
            base, ext = os.path.splitext(filename)
            mp3_filename = base + '.mp3'

            bot.edit_message_text("📤 သီချင်းတွေ့ပြီ၊ ပို့ပေးနေပြီ...", chat_id, sent_msg.message_id)
            
            # Telegram ထံ Audio ပို့ခြင်း
            with open(mp3_filename, 'rb') as audio:
                bot.send_audio(chat_id, audio, title=info.get('title'))
            
            # ဒေါင်းထားတဲ့ဖိုင်တွေကို ပြန်ဖျက်ခြင်း (Storage ချွေတာရန်)
            if os.path.exists(mp3_filename): os.remove(mp3_filename)
            if os.path.exists(filename) and filename != mp3_filename: os.remove(filename)
                
            bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ အမှား: {str(e)}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    bot.infinity_polling()

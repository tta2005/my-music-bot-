import os
import telebot
import yt_dlp
from telebot import types

# မင်းရဲ့ နောက်ဆုံး Token အသစ်
API_TOKEN = '8459123928:AAGzz59AXJxL0WMUL_2ePF4jRs2nvAIDQq8'
bot = telebot.TeleBot(API_TOKEN)

user_data = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "နေကောင်းလား သားကြီး! သီချင်းနာမည် ဒါမှမဟုတ် YouTube Link ပို့ပေးပါ။")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text
    chat_id = message.chat.id
    user_data[chat_id] = query

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

    sent_msg = bot.send_message(chat_id, f"📥 {quality}kbps နဲ့ ပြင်ဆင်နေတယ်...")

    ydl_opts = {
        # Format ကို 'bestaudio' တစ်မျိုးတည်း မဟုတ်ဘဲ ပိုကျယ်ပြန့်အောင် ပြင်ထားတယ်
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt', 
        'noplaylist': True,
        'quiet': False,
        # Signature/Cipher Error တွေအတွက် အောက်ကဟာလေး ထည့်ပေးထားတယ်
        'extract_flat': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch1:{query}" if not query.startswith('http') else query
            # ရှာဖွေပြီး အချက်အလက်ယူခြင်း
            info = ydl.extract_info(search_query, download=True)
            
            if 'entries' in info:
                info = info['entries'][0]
            
            filename = ydl.prepare_filename(info)
            base, ext = os.path.splitext(filename)
            mp3_filename = base + '.mp3'

            bot.edit_message_text("📤 သီချင်းတွေ့ပြီ၊ ပို့ပေးနေပြီ...", chat_id, sent_msg.message_id)
            
            with open(mp3_filename, 'rb') as audio:
                bot.send_audio(chat_id, audio, title=info.get('title'))
            
            # ဖိုင်ဟောင်းတွေ ရှင်းထုတ်ခြင်း
            if os.path.exists(mp3_filename): os.remove(mp3_filename)
            if os.path.exists(filename) and filename != mp3_filename: os.remove(filename)
            
            bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        error_msg = str(e)
        if "Requested format is not available" in error_msg:
             bot.edit_message_text("❌ ဒီသီချင်းက MP3 ပြောင်းလို့မရတဲ့ အမျိုးအစားဖြစ်နေတယ်၊ တခြားဟာ စမ်းကြည့်ပါဦး။", chat_id, sent_msg.message_id)
        elif "Sign in to confirm" in error_msg:
            bot.edit_message_text("❌ YouTube က Block ထားလို့ cookies.txt အသစ် လဲပေးပါဦး။", chat_id, sent_msg.message_id)
        else:
            bot.edit_message_text(f"❌ Error: {error_msg[:100]}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    # Connection reset ပြဿနာအတွက် retry ပါတဲ့ polling ကို သုံးထားတယ်
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

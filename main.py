import os
import telebot
import yt_dlp

# မင်းရဲ့ Bot Token ကို ကုဒ်ထဲမှာ တိုက်ရိုက်ထည့်ထားပါတယ်
API_TOKEN = '8459123928:AAFREMWam1sdTZCgS5ieHnJ3N0pz1smbvmo'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "နေကောင်းလား သားကြီး! သီချင်းနာမည် ဒါမှမဟုတ် YouTube Link ပို့ပေးပါ။ ငါ ရှာပေးမယ်။")

@bot.message_handler(func=lambda message: True)
def download_music(message):
    query = message.text
    chat_id = message.chat.id
    
    sent_msg = bot.send_message(chat_id, f"🔎 '{query}' ကို YouTube မှာ ရှာနေတယ် ခဏစောင့်နော်...")

    # yt-dlp options (YouTube ပိတ်တာ ကျော်ဖို့ cookies.txt ကို သုံးထားတယ်)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'cookiefile': 'cookies.txt',  # GitHub မှာ တင်ထားတဲ့ ဖိုင်နာမည်က cookies.txt ဖြစ်ရပါမယ်
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ရှာဖွေပြီး အချက်အလက်ယူခြင်း
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            if 'entries' in info:
                info = info['entries'][0]
            
            # ဖိုင်နာမည် သတ်မှတ်ခြင်း
            filename = ydl.prepare_filename(info)
            base, ext = os.path.splitext(filename)
            mp3_filename = base + '.mp3'

            bot.edit_message_text("📤 သီချင်းတွေ့ပြီ၊ ပို့ပေးနေပြီ...", chat_id, sent_msg.message_id)
            
            # သီချင်းကို Telegram ဆီ ပို့ခြင်း
            with open(mp3_filename, 'rb') as audio:
                bot.send_audio(chat_id, audio, title=info.get('title'))
            
            # Storage မပြည့်အောင် ဖိုင်တွေကို ပြန်ဖျက်ခြင်း
            if os.path.exists(mp3_filename):
                os.remove(mp3_filename)
            if os.path.exists(filename):
                os.remove(filename)
                
            bot.delete_message(chat_id, sent_msg.message_id)

    except Exception as e:
        error_msg = str(e)
        if "Sign in to confirm you're not a bot" in error_msg:
            bot.edit_message_text("❌ YouTube က ပိတ်လိုက်ပြန်ပြီ။ Cookies အသစ် ပြန်တင်ပေးပါဦး သားကြီး။", chat_id, sent_msg.message_id)
        else:
            bot.edit_message_text(f"❌ အမှားအယွင်း ရှိသွားတယ်: {error_msg}", chat_id, sent_msg.message_id)

if __name__ == "__main__":
    print("🚀 Bot ကို Cloud ပေါ်မှာ အောင်မြင်စွာ စတင်လိုက်ပါပြီ!")
    bot.infinity_polling()

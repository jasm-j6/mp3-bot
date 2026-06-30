import os
import re
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import requests

# 1. إعداد خادم الويب الخفيف لمنع نوم السيرفر على Render
app = Flask("")

@app.route("/")
def home():
    return "سيرفر البوت مستقر ويعمل بأعلى كفاءة لتعديل الملفات الصوتية! 🛡️🎵"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# 2. جلب التوكن بشكل آمن ومحمي من البيئة المحيطة (Environment Variable)
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@qafia2"
DEFAULT_RIGHTS = "تم التعديل بأعلى كفاءة بواسطة  @Mp3_EdBot 🎵"

bot = telebot.TeleBot(TOKEN)
user_data = {}

def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return True

def send_sub_msg(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("انضمام للقناة 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("التحقق من الاشتراك ✅", callback_data="check_subscription"))
    bot.send_message(
        chat_id,
        f"⚠️ عذراً عزيزي، يجب عليك الاشتراك في قناة البوت أولاً لاستخدام الميزات الملوكية:\n\n{CHANNEL_USERNAME}\n\nاشترك ثم اضغط على زر التحقق بالأسفل 👇",
        reply_markup=markup,
    )

@bot.message_handler(commands=["cancel"])
def cancel_action(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        user_data.pop(chat_id)
    bot.reply_to(message, "تم إلغاء العملية الحالية بنجاح 🛑\nيمكنك إرسال ملف صوتي جديد في أي وقت.")

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    chat_id = message.chat.id
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return
    bot.reply_to(
        message,
        "أهلاً بك في النسخة المستقرة والمعتمدة بالكامل! 🎵🛡️\n\n"
        "💡 **الميزة الحالية:**\n"
        "**تعديل الملفات الصوتية:** أرسل ملفك الـ MP3 مباشرة وعدل غلافه، وحقوقه، واسم الفنان، والوصف بسلاسة تامة وبأعلى جودة.\n\n"
        "أرسل ملفك الصوتي الآن لنبدأ العمل فوراً!",
    )

@bot.message_handler(commands=["clean"])
def clean_unused_files(message):
    chat_id = message.chat.id
    audio_path = f"final_{chat_id}.mp3"
    photo_path = f"thumb_{chat_id}.jpg"
    if os.path.exists(audio_path): os.remove(audio_path)
    if os.path.exists(photo_path): os.remove(photo_path)
    bot.reply_to(message, "تمت صيانة وتنظيف الملفات المؤقتة بنجاح 🧹")

@bot.message_handler(content_types=["audio", "document"])
def handle_audio(message):
    chat_id = message.chat.id
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return

    file_info = None
    if message.content_type == "audio":
        file_info = message.audio
    elif message.content_type == "document" and message.document.mime_type.startswith("audio/"):
        file_info = message.document

    if not file_info:
        bot.reply_to(message, "الرجاء أرسل ملف صوتی صالح! ❌")
        return

    # فحص حجم الملف فوراً قبل البدء بالمعالجة لحماية السيرفر وتنبيه المستخدم
    if getattr(file_info, "file_size", 0) > 49 * 1024 * 1024:
        bot.reply_to(
            message, 
            "⚠️ **تنبيه بخصوص الملفات الكبيرة:**\n"
            "الملف الذي أرسلته يتجاوز حد الـ 50 ميجابايت المسموح به من نظام تيليجرام للبوتات العادية.\n"
            "الرجاء إرسال ملف أصغر حجماً ليتمكن البوت من معالجته بنجاح! ❌"
        )
        return

    user_data[chat_id] = {
        "file_id": file_info.file_id,
        "orig_title": getattr(file_info, "title", "صوت معدل"),
        "orig_artist": getattr(file_info, "performer", "صوتيات فخمة"),
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي والإبقاء على الأصل ⏭️", callback_data="skip_title"))
    msg = bot.send_message(chat_id, "وصل الملف بنجاح! ✅\n\nأرسل الآن **العنوان الجديد** للملف، أو اضغط تخطي:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_title)

def get_title(message):
    chat_id = message.chat.id
    if message.text == "/cancel" or not check_sub(message.from_user.id): return
    if "title" not in user_data.get(chat_id, {}): user_data.setdefault(chat_id, {})["title"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي وإبقاء الأصل ⏭️", callback_data="skip_artist"))
    msg = bot.send_message(chat_id, "ممتاز! الآن أرسل **اسم الفنان (المطرب)**، أو اضغط تخطي:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_artist)

def get_artist(message):
    chat_id = message.chat.id
    if message.text == "/cancel" or not check_sub(message.from_user.id): return
    if "artist" not in user_data.get(chat_id, {}): user_data.setdefault(chat_id, {})["artist"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("استخدام الحقوق الافتراضية 📝", callback_data="skip_desc"))
    msg = bot.send_message(chat_id, "رائع! الآن أرسل **الوصف أو الحقوق**، أو اضغط الزر للحقوق الافتراضية:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_description)

def get_description(message):
    chat_id = message.chat.id
    if message.text == "/cancel" or not check_sub(message.from_user.id): return
    if "desc" not in user_data.get(chat_id, {}): user_data.setdefault(chat_id, {})["desc"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo"))
    msg = bot.send_message(chat_id, "أخيراً، أرسل **الصورة المصغرة (الغلاف)**، أو اضغط زر التخطي:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_photo)

def get_photo(message):
    chat_id = message.chat.id
    if message.text == "/cancel" or not check_sub(message.from_user.id): return

    is_skipped = "photo_skipped" in user_data.get(chat_id, {})
    if message.content_type != "photo" and not is_skipped:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo"))
        bot.send_message(chat_id, "الرجاء إرسال صورة صالحة أو الضغط على زر التخطي:", reply_markup=markup)
        bot.register_next_step_handler(message, get_photo)
        return

    bot.send_message(chat_id, "جاري معالجة وتجهيز ملفك الصوتي الفخم... انتظر ثوانٍ ⏳")
    audio_path = f"final_{chat_id}.mp3"
    photo_path = f"thumb_{chat_id}.jpg"

    try:
        raw_file_id = user_data[chat_id]["file_id"]
        file_info = bot.get_file(raw_file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        with requests.get(file_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(audio_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=16384):
                    f.write(chunk)

        has_photo = False
        if not is_skipped:
            photo_id = message.photo[-1].file_id
            photo_info = bot.get_file(photo_id)
            downloaded_photo = bot.download_file(photo_info.file_path)
            with open(photo_path, "wb") as f:
                f.write(downloaded_photo)
            has_photo = True

        final_title = user_data[chat_id]["title"] if user_data[chat_id].get("title") else user_data[chat_id]["orig_title"]
        final_artist = user_data[chat_id]["artist"] if user_data[chat_id].get("artist") else user_data[chat_id]["orig_artist"]
        caption_text = f"🔥 {user_data[chat_id]['desc']}" if user_data[chat_id].get("desc") else f"✅ {DEFAULT_RIGHTS}"

        with open(audio_path, "rb") as audio_file:
            if has_photo and os.path.exists(photo_path):
                with open(photo_path, "rb") as thumb_file:
                    bot.send_audio(chat_id=chat_id, audio=audio_file, title=final_title, performer=final_artist, thumb=thumb_file, caption=caption_text, timeout=300)
            else:
                bot.send_audio(chat_id=chat_id, audio=audio_file, title=final_title, performer=final_artist, caption=caption_text, timeout=300)

        # تنظيف فوري ومؤكد للملفات لتوفير مساحة السيرفر
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(photo_path): os.remove(photo_path)
        if chat_id in user_data: user_data.pop(chat_id)

    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ أثناء المعالجة السحابية: {str(e)}\nيرجى إعادة المحاولة.")
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(photo_path): os.remove(photo_path)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if not check_sub(message.from_user.id):
        send_sub_msg(message.chat.id)
        return
    bot.reply_to(message, "🎤 أرسل لي ملفاً صوتياً بصيغة MP3 مباشرة لكي نقوم بتعديل حقوقه وغلافه فوراً!")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.data == "check_subscription":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "تم تأكيد الاشتراك بنجاح! 🎉")
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, "أرسل الآن الملف الصوتي لبدء العمل الفوري 🎵")
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد.", show_alert=True)
    elif call.data == "skip_title":
        user_data.setdefault(chat_id, {})["title"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_title(call.message)
    elif call.data == "skip_artist":
        user_data.setdefault(chat_id, {})["artist"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_artist(call.message)
    elif call.data == "skip_desc":
        user_data.setdefault(chat_id, {})["desc"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_description(call.message)
    elif call.data == "skip_photo":
        user_data.setdefault(chat_id, {})["photo_skipped"] = True
        bot.clear_step_handler_by_chat_id(chat_id)
        get_photo(call.message)

if __name__ == "__main__":
    print("🚀 تشغيل السيرفر بالنسخة المستقرة المخصصة للملفات...")
    keep_alive()
    bot.infinity_polling(timeout=40, long_polling_timeout=20)

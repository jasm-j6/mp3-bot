import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# 1. خادم ويب خفيف للحفاظ على استقرار Render لمنع الكراش
app = Flask("")

@app.route("/")
def home():
    return "السيرفر الذكي السحابي يعمل بأعلى كفاءة وبدون حدود للأحجام! 🚀🎵"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# 2. إعدادات التوكن والقنوات
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@qafia2"
DEFAULT_RIGHTS = "تم التعديل بنجاح وبأعلى كفاءة سحابية بواسطة @Mp3_EdBot 🎵"

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

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    chat_id = message.chat.id
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return
    bot.reply_to(
        message,
        "مرحباً بك مجدداً! 🎧 البوت جاهز تماماً للعمل.\n\n"
        "🛠️ طـريـقـة الـعـمـل:\n"
        "1️⃣ أرسل الملف الصوتي (MP3) المراد تعديله هنا.\n"
        "2️⃣ أرسل العنوان الجديد، أو اضغط (تخطي) للإبقاء على الأصل.\n"
        "3️⃣ أرسل اسم الفنان (المطرب)، أو اضغط (تخطي).\n"
        "4️⃣ اكتب الحقوق أو الوصف النصي الذي تريده تحت الملف.\n"
        "5️⃣ أرسل غلاف الملف (الصورة المصغرة)، أو اضغط (تخطي).\n\n"
        "🚀 سيتولى البوت المعالجة السحابية الفورية ويعيد إليك ملفك فخماً ومعدلاً في ثوانٍ!\n\n"
        "بانتظار ملفك الصوتي الأول الآن... 📥"
    )

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
        bot.reply_to(message, "الرجاء أرسل ملف صوتي صالح! ❌")
        return

    # حفظ مراجع الملف دون تحميله للحفاظ على موارد السيرفر
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
    if chat_id not in user_data: return
    if "title" not in user_data[chat_id]: user_data[chat_id]["title"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي وإبقاء الأصل ⏭️", callback_data="skip_artist"))
    msg = bot.send_message(chat_id, "ممتاز! الآن أرسل **اسم الفنان (المطرب)**، أو اضغط تخطي:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_artist)

def get_artist(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    if "artist" not in user_data[chat_id]: user_data[chat_id]["artist"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("استخدام الحقوق الافتراضية 📝", callback_data="skip_desc"))
    msg = bot.send_message(chat_id, "رائع! الآن أرسل **الوصف أو الحقوق**، أو اضغط الزر للحقوق الافتراضية:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_description)

def get_description(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    if "desc" not in user_data[chat_id]: user_data[chat_id]["desc"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo"))
    msg = bot.send_message(chat_id, "أخيراً، أرسل **الصورة المصغرة (الغلاف)**، أو اضغط زر التخطي:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_photo)
def get_photo(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    
    is_skipped = "photo_skipped" in user_data[chat_id]
    if message.content_type != "photo" and not is_skipped:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo"))
        bot.send_message(chat_id, "الرجاء إرسال صورة صالحة أو الضغط على زر التخطي:", reply_markup=markup)
        bot.register_next_step_handler(message, get_photo)
        return

    status_msg = bot.send_message(chat_id, "جاري معالجة وتعديل الحقوق سحابياً... ⏳")

    try:
        # جلب البيانات المدخلة أو الحفاظ على الأصول
        final_title = user_data[chat_id]["title"] if user_data[chat_id].get("title") else user_data[chat_id]["orig_title"]
        final_artist = user_data[chat_id]["artist"] if user_data[chat_id].get("artist") else user_data[chat_id]["orig_artist"]
        caption_text = f"🔥 {user_data[chat_id]['desc']}" if user_data[chat_id].get("desc") else f"✅ {DEFAULT_RIGHTS}"
        
        # تجهيز الغلاف إذا أُرسل
        thumb_file_id = None
        if not is_skipped and message.photo:
            thumb_file_id = message.photo[-1].file_id

        # 🚀 إرسال الملف باستخدام ميزة التعديل الفوري المباشر عبر كائن الصوت
        audio_media = types.InputMediaAudio(
            media=user_data[chat_id]["file_id"],
            thumb=thumb_file_id,
            title=final_title,
            performer=final_artist,
            caption=caption_text
        )

        # إرسال المجموعة كـ Media Group لكسر الكاش القديم لتليجرام
        sent_messages = bot.send_media_group(chat_id=chat_id, media=[audio_media], timeout=300)

        # حذف رسالة الانتظار
        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدثت مشكلة أثناء المعالجة السحابية: {str(e)}", chat_id, status_msg.message_id)
    finally:
        user_data.pop(chat_id, None)

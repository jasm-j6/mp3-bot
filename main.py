import os
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import music_tag

app = Flask("")

@app.route("/")
def home():
    return "المحرك السحابي الذكي يعمل بأعلى كفاءة واستقرار! 🚀🎵"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_USERNAME = "@qafia2"
DEFAULT_RIGHTS = "تم التعديل بنجاح وبأعلى كفاءة سحابية بواسطة @Mp3_EdBot 🎵"

bot = telebot.TeleBot(TOKEN)
user_data = {}

MAX_FILE_SIZE = 20 * 1024 * 1024 

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
        "مرحباً بك في النسخة السحابية المستقرة والمطورة! 🎧\n\n"
        "ℹ️ **ملاحظة هامة:** البوت يعالج الآن الملفات حتى **20 ميجابايت** بأعلى كفاءة برمجية.\n\n"
        "🛠️ طـريـقـة الـعـمـل:\n"
        "1️⃣ أرسل الملف الصوتي (MP3) المراد تعديله هنا.\n"
        "2️⃣ أرسل العنوان الجديد، أو اضغط (تخطي).\n"
        "3️⃣ أرسل اسم الفنان (المطرب)، أو اضغط (تخطي).\n"
        "4️⃣ اكتب الحقوق أو الوصف النصي الذي تريده.\n"
        "5️⃣ أرسل غلاف الملف (الصورة المصغرة)، أو اضغط (تخطي).\n\n"
        "بانتظار ملفك الصوتي الآن... 📥"
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

    if file_info.file_size > MAX_FILE_SIZE:
        bot.reply_to(message, "⚠️ عذراً يا غالي، حجم الملف أكبر من 20 ميجابايت.")
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
    if chat_id not in user_data: return
    if message.text: user_data[chat_id]["title"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي وإبقاء الأصل ⏭️", callback_data="skip_artist"))
    msg = bot.send_message(chat_id, "ممتاز! الآن أرسل **اسم الفنان (المطرب)**، أو اضغط تخطي:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_artist)

def get_artist(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    if message.text: user_data[chat_id]["artist"] = message.text
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("استخدام الحقوق الافتراضية 📝", callback_data="skip_desc"))
    msg = bot.send_message(chat_id, "رائع! الآن أرسل **الوصف أو الحقوق**، أو اضغط الزر للحقوق الافتراضية:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_description)

def get_description(message):
    chat_id = message.chat.id
    if chat_id not in user_data: return
    if message.text: user_data[chat_id]["desc"] = message.text
    
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

    status_msg = bot.send_message(chat_id, "جاري المعالجة السحابية المتقدمة وحقن البيانات... ⏳")

    audio_path = f"audio_{chat_id}.mp3"
    photo_path = f"thumb_{chat_id}.jpg"

    try:
        final_title = user_data[chat_id].get("title") or user_data[chat_id]["orig_title"]
        final_artist = user_data[chat_id].get("artist") or user_data[chat_id]["orig_artist"]
        caption_text = f"🔥 {user_data[chat_id]['desc']}" if user_data[chat_id].get("desc") else f"✅ {DEFAULT_RIGHTS}"
        
        # تحميل الملف الصوتي
        file_info = bot.get_file(user_data[chat_id]["file_id"])
        downloaded_file = bot.download_file(file_info.file_path)
        with open(audio_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # تحميل الصورة
        has_photo = False
        if not is_skipped and message.photo:
            photo_info = bot.get_file(message.photo[-1].file_id)
            downloaded_photo = bot.download_file(photo_info.file_path)
            with open(photo_path, 'wb') as p_file:
                p_file.write(downloaded_photo)
            has_photo = True

        # 🦾 معالجة مرنة وسهلة باستخدام music-tag لتفادي مشاكل الفريمات
        f = music_tag.load_file(audio_path)
        f['title'] = final_title
        f['artist'] = final_artist
        
        if has_photo:
            with open(photo_path, "rb") as img_file:
                f['artwork'] = img_file.read()
        
        f.save()

        # إرسال الملف المعدل والنهائي للمستخدم
        with open(audio_path, 'rb') as audio_to_send:
            bot.send_audio(
                chat_id=chat_id,
                audio=audio_to_send,
                title=final_title,
                performer=final_artist,
                caption=caption_text,
                timeout=300
            )

        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدثت مشكلة أثناء المعالجة: {str(e)}", chat_id, status_msg.message_id)
    finally:
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(photo_path): os.remove(photo_path)
        user_data.pop(chat_id, None)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.data == "check_subscription":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "تم تأكيد الاشتراك! 🎉")
            bot.delete_message(chat_id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك بالقناة بعد.", show_alert=True)
    elif call.data in ["skip_title", "skip_artist", "skip_desc", "skip_photo"]:
        key = call.data.replace("skip_", "")
        if key == "photo": user_data.setdefault(chat_id, {})["photo_skipped"] = True
        else: user_data.setdefault(chat_id, {})[key] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        if call.data == "skip_title": get_title(call.message)
        elif call.data == "skip_artist": get_artist(call.message)
        elif call.data == "skip_desc": get_description(call.message)
        elif call.data == "skip_photo": get_photo(call.message)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=50, long_polling_timeout=25)

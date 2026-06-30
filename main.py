import os
import requests
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# 1. إعداد خادم الويب لمنع نوم أو كراش السيرفر على Render
app = Flask("")

@app.route("/")
def home():
    return "سيرفر البوت مستقر ويعمل بأعلى كفاءة لجميع الأحجام! 🛡️🎵"

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

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    chat_id = message.chat.id
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return
    bot.reply_to(
        message,
        "أهلاً بك في النسخة الملوكية المحدثة! 🎵🛡️\n\n"
        "البوت الآن جاهز لاستقبال الملفات الصوتية **بجميع الأحجام (الصغيرة والكبيرة)** لتعديل حقوقها وغلافها فوراً دون قيود.",
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

    # حفظ بيانات الملف للبدء في خطوات التعديل
    user_data[chat_id] = {
        "file_id": file_info.file_id,
        "orig_title": getattr(file_info, "title", "صوت معدل"),
        "orig_artist": getattr(file_info, "performer", "صوتيات فخمة"),
        "file_size": file_info.file_size
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

    status_msg = bot.send_message(chat_id, "جاري معالجة وتحميل ملفك الفخم مهما كان حجمه... انتظر ثوانٍ ⏳")
    audio_path = f"final_{chat_id}.mp3"
    photo_path = f"thumb_{chat_id}.jpg"

    try:
        raw_file_id = user_data[chat_id]["file_id"]
        
        # 💡 الخدعة الهندسية: جلب مسار الملف مباشرة عبر طلب سحابي لتخطي حد الـ 20 ميجابايت الخاص بالمكتبة
        res = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={raw_file_id}").json()
        
        if res.get("ok"):
            file_path = res["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
            
            # تحميل الملف الصوتي على شكل دفق (Stream Chunks) للحفاظ على السيرفر من الكراش
            with requests.get(file_url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(audio_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=131072): # 128kb chunks لأعلى سرعة
                        f.write(chunk)
        else:
            raise Exception("فشل نظام التحميل السحابي المباشر لتيليجرام")

        has_photo = False
        if not is_skipped and message.photo:
            photo_id = message.photo[-1].file_id
            photo_info = bot.get_file(photo_id)
            downloaded_photo = bot.download_file(photo_info.file_path)
            with open(photo_path, "wb") as f:
                f.write(downloaded_photo)
            has_photo = True

        final_title = user_data[chat_id]["title"] if user_data[chat_id].get("title") else user_data[chat_id]["orig_title"]
        final_artist = user_data[chat_id]["artist"] if user_data[chat_id].get("artist") else user_data[chat_id]["orig_artist"]
        caption_text = f"🔥 {user_data[chat_id]['desc']}" if user_data[chat_id].get("desc") else f"✅ {DEFAULT_RIGHTS}"

        bot.edit_message_text("جاري إعادة رفع الملف المعدل بأعلى جودة... 🚀", chat_id, status_msg.message_id)

        # الرفع الذكي والمباشر لتفادي حدود الـ 50 ميجابايت عند الحاجة
        with open(audio_path, "rb") as audio_file:
            if user_data[chat_id]["file_size"] > 48 * 1024 * 1024:
                # رفع كملف وثيقة لتخطي جدار الصوتيات التلقائي للملفات الكبيرة
                bot.send_document(
                    chat_id=chat_id,
                    document=audio_file,
                    caption=f"🎵 {final_title} - {final_artist}\n\n{caption_text}",
                    timeout=600
                )
            else:
                if has_photo and os.path.exists(photo_path):
                    with open(photo_path, "rb") as thumb_file:
                        bot.send_audio(chat_id, audio_file, title=final_title, performer=final_artist, thumb=thumb_file, caption=caption_text, timeout=300)
                else:
                    bot.send_audio(chat_id, audio_file, title=final_title, performer=final_artist, caption=caption_text, timeout=300)

        bot.delete_message(chat_id, status_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء المعالجة: {str(e)}\nيرجى محاولة رفع الملف من جديد.", chat_id, status_msg.message_id)
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
    elif call.data == "skip_title":
        if chat_id in user_data: user_data[chat_id]["title"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_title(call.message)
    elif call.data == "skip_artist":
        if chat_id in user_data: user_data[chat_id]["artist"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_artist(call.message)
    elif call.data == "skip_desc":
        if chat_id in user_data: user_data[chat_id]["desc"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_description(call.message)
    elif call.data == "skip_photo":
        if chat_id in user_data: user_data[chat_id]["photo_skipped"] = True
        bot.clear_step_handler_by_chat_id(chat_id)
        get_photo(call.message)

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(timeout=50, long_polling_timeout=25)

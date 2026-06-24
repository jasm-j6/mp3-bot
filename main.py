import os
import re
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import requests

# 1. إعداد سيرفر ويب متوافق مع Render لمنع توقف البوت
app = Flask("")

@app.route("/")
def home():
    return "البوت يعمل بكفاءة ملوكية ودائمة على سيرفر Render! 🚀"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# 2. الإعدادات الأساسية للبوت
TOKEN = "8889690063:AAFgia5rX0Ac2wFWRFxFSlITgSUHOaaKU4g"
CHANNEL_USERNAME = "@qafia2"
DEFAULT_RIGHTS = "تم التعديل بأعلى كفاءة بواسطة  @Mp3_EdBot 🎵"

bot = telebot.TeleBot(TOKEN)
user_data = {}

# دالة للتحقق مما إذا كانت الرسالة تحتوي على رابط ويب (URL)
def is_url(text):
    url_pattern = re.compile(r'https?://(?:www\.)?\S+')
    return bool(url_pattern.search(text))

# دالة التحقق اللحظي من الاشتراك الإجباري
def check_sub(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception:
        return True

def send_sub_msg(chat_id):
    markup = types.InlineKeyboardMarkup()
    btn_link = types.InlineKeyboardButton(
        "Anjoin القناة 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    )
    btn_check = types.InlineKeyboardButton(
        "التحقق من الاشتراك ✅", callback_data="check_subscription"
    )
    markup.add(btn_link)
    markup.add(btn_check)
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
    bot.reply_to(
        message,
        "تم إلغاء العملية الحالية بنجاح 🛑\nيمكنك إرسال ملف صوتي أو رابط جديد في أي وقت.",
    )

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    chat_id = message.chat.id
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return

    bot.reply_to(
        message,
        "أهلاً بك في بوت تعديل وتحميل الصوتيات المحترف! 🎵\n\n"
        "💡 **طريقة الاستخدام:**\n"
        "1- **لتعديل ملفك:** أرسل لي أي ملف صوتي (MP3) ثم تفاعل مع الأزرار الشفافة.\n"
        "2- **للتحميل من رابط:** أرسل لي رابط الويب مباشرة (يوتيوب، فيسبوك، إلخ) وسأقوم باستخراج الصوت فوراً!\n"
        "3- لإلغاء العملية في أي وقت أرسل الأمر /cancel .\n\n"
        "أرسل ملفك أو الرابط الآن لنبدأ فوراً!",
    )

# دالة التحميل المحدثة باستخدام خوادم Cobalt العالمية الفخمة والمستقرة
def handle_url_download(message):
    chat_id = message.chat.id
    url = message.text.strip()
    
    status_msg = bot.reply_to(message, "جاري معالجة الرابط عبر خوادم متطورة وسريعة جداً... انتظر ثوانٍ ⏳")
    
    # إعداد الطلب لنظام Cobalt المخصص لاستخراج الصوت بجودة احترافية عالية
    api_url = "https://api.cobalt.tools/api/json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "downloadMode": "audio",  # استخراج الصوت فقط بدقة عالية جداً
        "audioFormat": "mp3",     # جلب الملف بصيغة mp3 مباشرة
        "audioBitrate": "320"     # أعلى جودة صوتية ممكنة
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # التحقق من حالة الملف وتوفر رابط التحميل المباشر
            if data.get("status") == "stream" or "url" in data:
                download_link = data["url"]
                # محاولة جلب العنوان أو تسميته باسم فخم افتراضي
                title = data.get("filename", "صوت مستخرج فخم")
                title = os.path.splitext(title)[0] # إزالة الامتداد من النص لو وجد
                
                bot.edit_message_text("جاري الآن رفع الصوت الملوكي المستخرج إلى تيليجرام... 🚀", chat_id, status_msg.message_id)
                
                # تحميل الملف بصيغة Stream ملوكية ورفعه مباشرة لحماية ذاكرة السيرفر
                audio_response = requests.get(download_link, stream=True, timeout=120)
                if audio_response.status_code == 200:
                    bot.send_audio(
                        chat_id=chat_id,
                        audio=audio_response.raw,
                        title=title,
                        performer=DEFAULT_RIGHTS,
                        caption=f"✅ تم التحميل بنجاح بواسطة البوت الملوكي\n👉 {DEFAULT_RIGHTS}",
                        timeout=120
                    )
                    bot.delete_message(chat_id, status_msg.message_id)
                else:
                    bot.edit_message_text("❌ تعذر تحميل الملف الصوتي من خادم المعالجة الأساسي.", chat_id, status_msg.message_id)
            elif data.get("status") == "error":
                bot.edit_message_text(f"❌ خطأ من خادم التحويل: {data.get('error', 'الرابط غير مدعوم أو محمي')}", chat_id, status_msg.message_id)
            else:
                bot.edit_message_text("❌ لم نتمكن من معالجة هذا الرابط حالياً، تأكد من صحته.", chat_id, status_msg.message_id)
        else:
            bot.edit_message_text("❌ خوادم التحويل العالمية مشغولة حالياً، يرجى إعادة المحاولة بعد دقيقة.", chat_id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ حدث خطأ أثناء الاتصال بالخادم الذكي: {str(e)}\nيرجى التحقق من الرابط لاحقاً.", chat_id, status_msg.message_id)

# معالج النصوص الذكي: يميز تلقائياً بين الروابط والـ Text العادي الخاص بالخطوات
@bot.message_handler(content_types=["text"])
def handle_text(message):
    chat_id = message.chat.id
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return
        
    if is_url(message.text):
        handle_url_download(message)
    else:
        pass

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

    user_data[chat_id] = {
        "file_id": file_info.file_id,
        "orig_title": getattr(file_info, "title", "صوت معدل"),
        "orig_artist": getattr(file_info, "performer", "صوتيات فخمة"),
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي والإبقاء على الأصل ⏭️", callback_data="skip_title"))

    msg = bot.send_message(
        chat_id,
        "وصل الملف بنجاح! ✅\n\nأرسل الآن **العنوان الجديد** للملف، أو اضغط على زر التخطي بالأسفل:\n(لإلغاء العملية أرسل /cancel)",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, get_title)

def get_title(message):
    chat_id = message.chat.id
    if message.text == "/cancel":
        return
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return

    if "title" not in user_data.get(chat_id, {}):
        user_data.setdefault(chat_id, {})["title"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي وإبقاء الأصل ⏭️", callback_data="skip_artist"))
    msg = bot.send_message(
        chat_id,
        "ممتاز! الآن أرسل **اسم الفنان (المطرب)**، أو اضغط على زر التخطي:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, get_artist)

def get_artist(message):
    chat_id = message.chat.id
    if message.text == "/cancel":
        return
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return

    if "artist" not in user_data.get(chat_id, {}):
        user_data.setdefault(chat_id, {})["artist"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("استخدام الحقوق الافتراضية 📝", callback_data="skip_desc"))
    msg = bot.send_message(
        chat_id,
        "رائع! الآن أرسل **الوصف أو الحقوق**، أو اضغط على الزر لاستخدام الحقوق الافتراضية:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, get_description)

def get_description(message):
    chat_id = message.chat.id
    if message.text == "/cancel":
        return
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return

    if "desc" not in user_data.get(chat_id, {}):
        user_data.setdefault(chat_id, {})["desc"] = message.text

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo"))
    msg = bot.send_message(
        chat_id,
        "أخيراً، أرسل **الصورة المصغرة (الغلاف)**، أو اضغط زر التخطي لتوليد الملف بدون بوستر:",
        reply_markup=markup,
    )
    bot.register_next_step_handler(msg, get_photo)

def get_photo(message):
    chat_id = message.chat.id
    if message.text == "/cancel":
        return
    if not check_sub(message.from_user.id):
        send_sub_msg(chat_id)
        return

    is_skipped = "photo_skipped" in user_data.get(chat_id, {})

    if message.content_type != "photo" and not is_skipped:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo"))
        bot.send_message(
            chat_id,
            "الرجاء إرسال صورة صالحة أو الضغط على زر التخطي:",
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, get_photo)
        return

    bot.send_message(chat_id, "جاري معالجة وتجهيز الملف الفخم... انتظر ثوانٍ معدودة ⏳")
    audio_path = f"final_{chat_id}.mp3"
    photo_path = f"thumb_{chat_id}.jpg"

    try:
        raw_file_id = user_data[chat_id]["file_id"]
        file_info = bot.get_file(raw_file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"

        with requests.get(file_url, stream=True) as r:
            r.raise_for_status()
            with open(audio_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
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
                    bot.send_audio(
                        chat_id=chat_id,
                        audio=audio_file,
                        title=final_title,
                        performer=final_artist,
                        thumb=thumb_file,
                        caption=caption_text,
                        timeout=120
                    )
            else:
                bot.send_audio(
                    chat_id=chat_id,
                    audio=audio_file,
                    title=final_title,
                    performer=final_artist,
                    caption=caption_text,
                    timeout=120
                )

        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(photo_path): os.remove(photo_path)
        if chat_id in user_data: user_data.pop(chat_id)

    except Exception as e:
        bot.send_message(chat_id, f"❌ حدث خطأ غير متوقع: {str(e)}")
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(photo_path): os.remove(photo_path)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id = call.message.chat.id
    if call.data == "check_subscription":
        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, "تم تأكيد الاشتراك بنجاح! 🎉")
            bot.delete_message(chat_id, call.message.message_id)
            bot.send_message(chat_id, "شكرًا لانضمامك! أرسل الآن الملف الصوتي أو الرابط لبدء العمل 🎵")
        else:
            bot.answer_callback_query(call.id, "❌ لم تشترك في القناة بعد، رجاءً اشترك واضغط مجدداً.", show_alert=True)
    elif call.data == "skip_title":
        bot.answer_callback_query(call.id, "تم التخطي")
        user_data.setdefault(chat_id, {})["title"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_title(call.message)
    elif call.data == "skip_artist":
        bot.answer_callback_query(call.id, "تم التخطي")
        user_data.setdefault(chat_id, {})["artist"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_artist(call.message)
    elif call.data == "skip_desc":
        bot.answer_callback_query(call.id, "تم تطبيق الحقوق الافتراضية")
        user_data.setdefault(chat_id, {})["desc"] = None
        bot.clear_step_handler_by_chat_id(chat_id)
        get_description(call.message)
    elif call.data == "skip_photo":
        bot.answer_callback_query(call.id, "تم التخطي بدون بوستر")
        user_data.setdefault(chat_id, {})["photo_skipped"] = True
        bot.clear_step_handler_by_chat_id(chat_id)
        get_photo(call.message)

# ==========================================
# تشغيل سيرفر Flask المخصص لمنصة Render
# ==========================================
def keep_alive_secure():
    port = int(os.environ.get("PORT", 10000))
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    t.daemon = True
    t.start()

# ==========================================
# نقطة الانطلاق الحاسمة للبوت (Polling)
# ==========================================
if __name__ == "__main__":
    print("⏳ جاري تهيئة سيرفر الويب لمنصة Render...")
    keep_alive_secure()
    
    print("🚀 البوت مستعد الآن ويستقبل الرسائل عبر نظام Cobalt العالمي...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)

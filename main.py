import os
from threading import Thread
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. إعداد خادم الويب الخفيف (Flask) لمنع نوم السيرفر على Render
app = Flask("")

@app.route("/")
def home():
    return "سيرفر البوت مستقر ويعمل بأعلى كفاءة لتعديل الملفات الصوتية الكبيرة جداً! 🛡️🎵"

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

# 2. جلب متغيرات البيئة الحساسة والمحمية من إعدادات Render
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

CHANNEL_USERNAME = "@qafia2"
DEFAULT_RIGHTS = "تم التعديل بأعلى كفاءة بواسطة  @Mp3_EdBot 🎵"

# تشغيل البوت بمحرك Pyrogram الخارق للملَّفات الكبيرة
bot = Client("audio_advanced_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_data = {}

async def check_sub(client, user_id):
    try:
        member = await client.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return True

async def send_sub_msg(client, chat_id):
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("انضمام للقناة 📢", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")],
        [InlineKeyboardButton("التحقق من الاشتراك ✅", callback_data="check_subscription")]
    ])
    await client.send_message(
        chat_id,
        f"⚠️ عذراً عزيزي، يجب عليك الاشتراك في قناة البوت أولاً لاستخدام الميزات الملوكية:\n\n{CHANNEL_USERNAME}\n\nاشترك ثم اضغط على زر التحقق بالأسفل 👇",
        reply_markup=markup
    )

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if not await check_sub(client, message.from_user.id):
        await send_sub_msg(client, message.chat.id)
        return
    await message.reply_text(
        "أهلاً بك في النسخة الملوكية الخارقة للملفات الضخمة! 🎵🛡️\n\n"
        "💡 **الميزة الحالية:**\n"
        "**تعديل الملفات الصوتية الكبيرة:** أرسل ملفك الـ MP3 مباشرة (حتى لو تجاوز 100 ميجابايت!) وعدل غلافه، وحقوقه بسلاسة تامّة.\n\n"
        "أرسل ملفك الصوتي الآن لنبدأ العمل فوراً!"
    )

@bot.on_message((filters.audio | filters.document) & filters.private)
async def handle_audio(client, message):
    chat_id = message.chat.id
    if not await check_sub(client, message.from_user.id):
        await send_sub_msg(client, chat_id)
        return

    # التحقق من نوع الملف والتأكد أنه صوتي
    file_info = message.audio if message.audio else message.document
    if message.document and not message.document.mime_type.startswith("audio/"):
        await message.reply_text("الرجاء أرسل ملف صوتی صالح! ❌")
        return

    # تخزين بيانات المعالجة المؤقتة في الذاكرة
    user_data[chat_id] = {
        "message_id": message.id,
        "orig_title": getattr(file_info, "title", "صوت معدل"),
        "orig_artist": getattr(file_info, "performer", "صوتيات فخمة"),
    }

    markup = InlineKeyboardMarkup([[InlineKeyboardButton("تخطي والإبقاء على الأصل ⏭️", callback_data="skip_title")]])
    await message.reply_text("وصل الملف الضخم بنجاح! ✅\n\nأرسل الآن **العنوان الجديد** للملف، أو اضغط تخطي:", reply_markup=markup)

@bot.on_message(filters.text & filters.private)
async def handle_text_steps(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return

    data = user_data[chat_id]
    
    # التحقق من الخطوة الحالية وتوجيه النص المدخل بشكل ديناميكي صحيح
    if "title" not in data:
        data["title"] = message.text
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("تخطي وإبقاء الأصل ⏭️", callback_data="skip_artist")]])
        await message.reply_text("ممتاز! الآن أرسل **اسم الفنان (المطرب)**، أو اضغط تخطي:", reply_markup=markup)
    elif "artist" not in data:
        data["artist"] = message.text
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("استخدام الحقوق الافتراضية 📝", callback_data="skip_desc")]])
        await message.reply_text("رائع! الآن أرسل **الوصف أو الحقوق**، أو اضغط الزر للحقوق الافتراضية:", reply_markup=markup)
    elif "desc" not in data:
        data["desc"] = message.text
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo")]])
        await message.reply_text("أخيراً، أرسل **الصورة المصغرة (الغلاف)**، أو اضغط زر التخطي:", reply_markup=markup)

@bot.on_message(filters.photo & filters.private)
async def handle_photo(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data or "desc" not in user_data[chat_id]:
        return

    status_msg = await message.reply_text("جاري تحميل ومعالجة الملف الضخم بنظام التدفق السريع... انتظر ثوانٍ ⏳")
    
    data = user_data[chat_id]
    audio_path = f"final_{chat_id}.mp3"
    photo_path = f"thumb_{chat_id}.jpg"

    try:
        # جلب الرسالة التي تحتوي على الملف الصوتي الأصلي للتحميل الآمن
        orig_msg = await client.get_messages(chat_id, data["message_id"])
        await client.download_media(orig_msg, file_name=audio_path)
        
        has_photo = False
        if "photo_skipped" not in data:
            await client.download_media(message.photo, file_name=photo_path)
            has_photo = True

        final_title = data["title"] if data.get("title") else data["orig_title"]
        final_artist = data["artist"] if data.get("artist") else data["orig_artist"]
        caption_text = f"🔥 {data['desc']}" if data.get("desc") else f"✅ {DEFAULT_RIGHTS}"

        await status_msg.edit_text("جاري إعادة رفع الملف الصوتي المعدل الفخم إلى تيليجرام... 🚀")

        # إرسال الملف الصوتي المعدل والجديد باستخدام تقنية دفق الملفات
        thumb = photo_path if has_photo else None
        await client.send_audio(
            chat_id=chat_id,
            audio=audio_path,
            title=final_title,
            performer=final_artist,
            thumb=thumb,
            caption=caption_text
        )

        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء المعالجة السحابية المتقدمة: {str(e)}")
    finally:
        # تنظيف فوري لملفات الخادم المؤقتة لتوفير المساحة ومقاومة كراش الذاكرة
        if os.path.exists(audio_path): os.remove(audio_path)
        if os.path.exists(photo_path): os.remove(photo_path)
        user_data.pop(chat_id, None)

@bot.on_callback_query()
async def handle_callbacks(client, call):
    chat_id = call.message.chat.id
    if call.data == "check_subscription":
        if await check_sub(client, call.from_user.id):
            await call.answer("تم تأكيد الاشتراك بنجاح! 🎉")
            await call.message.delete()
        else:
            await call.answer("❌ لم تشترك في القناة بعد.", show_alert=True)
            
    elif call.data == "skip_title":
        user_data.setdefault(chat_id, {})["title"] = None
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("تخطي وإبقاء الأصل ⏭️", callback_data="skip_artist")]])
        await call.message.edit_text("ممتاز! الآن أرسل **اسم الفنان (المطرب)**، أو اضغط تخطي:", reply_markup=markup)
        
    elif call.data == "skip_artist":
        user_data.setdefault(chat_id, {})["artist"] = None
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("استخدام الحقوق الافتراضية 📝", callback_data="skip_desc")]])
        await call.message.edit_text("رائع! الآن أرسل **الوصف أو الحقوق**، أو اضغط الزر للحقوق الافتراضية:", reply_markup=markup)
        
    elif call.data == "skip_desc":
        user_data.setdefault(chat_id, {})["desc"] = None
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("تخطي بدون بوستر ⏭️", callback_data="skip_photo")]])
        await call.message.edit_text("أخيراً، أرسل **الصورة المصغرة (الغلاف)**، أو اضغط زر التخطي:", reply_markup=markup)
        
    elif call.data == "skip_photo":
        user_data.setdefault(chat_id, {})["photo_skipped"] = True
        await call.message.edit_text("جاري المعالجة الفورية للملف الصوتي بدون بوستر... ⏳")
        # اصطناع كائن رسالة فارغ لمحاكاة الرفع المباشر دون توقف الكود
        class FakeMessage:
            photo = None
        await handle_photo(client, FakeMessage())

if __name__ == "__main__":
    print("🚀 المحرك السحابي الخارق قيد التشغيل للملفات الضخمة...")
    keep_alive()
    bot.run()

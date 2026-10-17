import telebot
from telebot import types

# Tokeningiz va o'zingizning Telegram ID raqamingiz
TOKEN = "8699727885:AAHWcstpPrG1kakmoIfWZ_EACCq..."
ADMIN_ID = 8846734228  # Sizning ID raqamingiz

bot = telebot.TeleBot(TOKEN)

# Kinolarni saqlash uchun lug'at (bazasi): { "kino_kodi": "file_id" }
MOVIES = {}

# /start buyrug'i
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if user_id == ADMIN_ID:
        # Admin uchun maxsus tugmali menyu
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🎬 Kino qo'shish"))
        bot.send_message(
            message.chat.id, 
            "Salom Admin! Xush kelibsiz. Quyidagi tugma orqali kino qo'shishingiz mumkin:", 
            reply_markup=markup
        )
    else:
        # Oddiy foydalanuvchilar uchun hech qanday menyu chiqmaydi (klaviatura tozalanadi)
        markup = types.ReplyKeyboardRemove()
        bot.send_message(
            message.chat.id, 
            "Salom! Kino kodini yuboring va kinoni tomosha qiling.", 
            reply_markup=markup
        )

# Admin "🎬 Kino qo'shish" tugmasini bosganda
@bot.message_handler(func=lambda message: message.text == "🎬 Kino qo'shish")
def ask_for_movie(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "Marhamat, kinoni (videoni) yuboring:")

# Video qabul qilish (Faqat ADMIN yuklay oladi)
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Kechirasiz, sizda video (kino) yuklash huquqi yo'q. Faqat admin kino qo'shishi mumkin.")
        return

    # Admin video yuborganda uni vaqtincha saqlab turamiz va kod so'raymiz
    file_id = message.video.file_id
    msg = bot.reply_to(message, "✅ Video qabul qilindi! Endi bu kino uchun **maxsus kod** (masalan: 1, 2 yoki film nomi) yuboring:")
    
    # Keyingi qadamda kodni qabul qilish uchun holatni saqlaymiz
    bot.register_next_step_handler(msg, save_movie_code, file_id)

# Kino kodini saqlab qolish funksiyasi
def save_movie_code(message, file_id):
    if message.from_user.id != ADMIN_ID:
        return
    
    code = message.text.strip()
    MOVIES[code] = file_id
    bot.reply_to(message, f"🎉 Kino muvaffaqiyatli saqlandi!\nKodi: `{code}`", parse_mode="Markdown")

# Matn kelganda (Oddiy foydalanuvchi kino kodini yuborsa yoki boshqa narsa yozsa)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    code = message.text.strip()
    
    # Agar kiritilgan kod bazada bo'lsa, kinoni yuboramiz
    if code in MOVIES:
        bot.send_video(message.chat.id, MOVIES[code], caption="Mana siz so'ragan kino! 🍿")
    else:
        bot.reply_to(message, "❌ Bunday kodli kino topilmadilti yoki noto'g'ri kod kiritdingiz.")

# Botni uzluksiz ishlatish
bot.infinity_polling()
    


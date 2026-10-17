import telebot
from telebot import types

TOKEN = "8699727885:AAHWcstpPrG1kakmoIfWZ_EACCq..."
ADMIN_ID = 8846734228  # Sizning ID raqamingiz

bot = telebot.TeleBot(TOKEN)

# Kinolar bazasi
MOVIES = {}

# /start buyrug'i
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    # Agar start bosgan odam ADMIN bo'lsa:
    if user_id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("🎬 Kino qo'shish")) # Faqat adminga ko'rinadigan tugma
        bot.send_message(message.chat.id, "Salom Admin! Xush kelibsiz. Quyidagi menyudan foydalanishingiz mumkin:", reply_markup=markup)
    else:
        # Agar ODDIY FOYDALANUVCHI bo'lsa - HECH QANDAY menyu chiqmaydi (klaviaturani tozalaymiz)
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Salom! Kino kodini yuboring va kinoni oling.", reply_markup=markup)

# Video yuborilganda (Faqat admin yuklay oladi)
@bot.message_handler(content_types=['video'])
def handle_video(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Kechirasiz, sizda video (kino) yuklash huquqi yo'q.")
        return

    bot.reply_to(message, "✅ Video qabul qilindi! Endi unga kino kodini yuborishingiz mumkin.")

# Oddiy matn yuborilganda (Kino izlash uchun)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text

    # Agar admin "🎬 Kino qo'shish" tugmasini bosgan bo'lsa
    if user_id == ADMIN_ID and text == "🎬 Kino qo'shish":
        bot.send_message(message.chat.id, "Zudlik bilan yuklamoqchi bo'lgan kinongizni (video formatida) yuboring:")
        return

    # Bu yerda oddiy foydalanuvchilar kino kodini yuborganda qidirish qismi ishlaydi
    bot.reply_to(message, f"Siz yuborgan kod bo'yicha kino qidirilmoqda: {text}")

bot.infinity_polling()



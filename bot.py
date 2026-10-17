import telebot
from telebot import types

TOKEN = "8699727885:AAHWcstpPprG1kakmoIfWZ_EACCq9_FcUAU"
ADMIN_ID = 8846734228
bot = telebot.TeleBot(TOKEN)

# Kinolar bazasi (file_id bilan birga)
MOVIES = {}

# Foydalanuvchilar va statistika
USERS = set()
user_state = {}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📥 Kino yuklash")
    btn2 = types.KeyboardButton("🗑 Kino o'chirish")
    btn3 = types.KeyboardButton("📋 Kinolar ro'yxati")
    btn4 = types.KeyboardButton("📊 Statistika")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    USERS.add(chat_id)
    user_state[chat_id] = None
    welcome_text = f"Salom, {message.from_user.first_name}! 🎬\nKino kodi yuboring yoki menyudan foydalaning:"
    bot.send_message(chat_id, welcome_text, reply_markup=main_menu())

# Menyu tugmalari va matnli xabarlar uchun handler
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    USERS.add(chat_id)
    text = message.text.strip()
    
    if text == "📋 Kinolar ro'yxati":
        user_state[chat_id] = None
        if not MOVIES:
            bot.send_message(chat_id, "📭 Hozircha kinolar ro'yxati bo'sh.", reply_markup=main_menu())
            return
        movie_list = "🎬 **Mavjud kinolar:**\n\n"
        for code, info in MOVIES.items():
            movie_list += f"🔹 Code: `{code}` - {info['title']}\n"
        bot.send_message(chat_id, movie_list, parse_mode="Markdown", reply_markup=main_menu())

    elif text == "📊 Statistika":
        user_state[chat_id] = None
        stats_text = (
            f"📊 **Bot statistikasi:**\n\n"
            f"👥 Foydalanuvchilar soni: **{len(USERS)}** ta\n"
            f"🎬 Kinolar soni: **{len(MOVIES)}** ta"
        )
        bot.send_message(chat_id, stats_text, parse_mode="Markdown", reply_markup=main_menu())

    elif text == "📥 Kino yuklash":
        user_state[chat_id] = "waiting_for_video"
        bot.send_message(
            chat_id, 
            "📥 Kino yuklash uchun **videoni yuboring** va uning izohiga (caption) quyidagi formatni yozing:\n\n"
            "`Kod | Nomi | Janri | Tavsifi`\n\n"
            "Masalan:\n`101 | Forsaj 9 | Jangari | Zo'r kino`", 
            parse_mode="Markdown"
        )

    elif text == "🗑 Kino o'chirish":
        user_state[chat_id] = "waiting_for_delete"
        bot.send_message(chat_id, "🗑 O'chirmoqchi bo'lgan kino **kodini** yuboring (masalan: `101`):", parse_mode="Markdown")

    elif user_state.get(chat_id) == "waiting_for_delete":
        if text in MOVIES:
            deleted_movie = MOVIES.pop(text)
            user_state[chat_id] = None
            bot.send_message(chat_id, f"✅ Muvaffaqiyatli o'chirildi!\nO'chirilgan kino: *{deleted_movie['title']}*", parse_mode="Markdown", reply_markup=main_menu())
        else:
            bot.send_message(chat_id, "❌ Bunday kodli kino topilmadi. Qaytadan to'g'ri kodni yuboring:")

    elif text in MOVIES:
        movie = MOVIES[text]
        response = (
            f"🎬 **Kino nomi:** {movie['title']}\n"
            f"🎭 **Janri:** {movie['genre']}\n"
            f"📝 **Tavsifi:** {movie['description']}\n\n"
            "🍿 Maroqli hordiq chiqaring!"
        )
        # Videoni va ma'lumotlarni yuborish
        if movie.get("file_id"):
            bot.send_video(chat_id, movie["file_id"], caption=response, parse_mode="Markdown")
        else:
            bot.send_message(chat_id, response, parse_mode="Markdown")

    else:
        bot.reply_to(message, "❌ Kechirasiz, bunday kodli kino topilmadi yoki buyruq tushunarsiz.")

# Video fayllarni qabul qilish uchun maxsus handler
@bot.message_handler(content_types=['video'])
def handle_video(message):
    chat_id = message.chat.id
    USERS.add(chat_id)
    
    if user_state.get(chat_id) == "waiting_for_video":
        caption = message.caption
        if not caption:
            bot.send_message(chat_id, "⚠️ Videoga izoh (caption) yozmadingiz! Iltimos, videoni qaytadan yuborib, izohiga formatni yozing: `Kod | Nomi | Janri | Tavsifi`", parse_mode="Markdown")
            return
        
        try:
            parts = caption.split("|")
            if len(parts) >= 4:
                code = parts[0].strip()
                title = parts[1].strip()
                genre = parts[2].strip()
                desc = parts[3].strip()
                file_id = message.video.file_id  # Telegram serveridagi video ID raqami
                
                MOVIES[code] = {
                    "title": title,
                    "genre": genre,
                    "description": desc,
                    "file_id": file_id
                }
                user_state[chat_id] = None
                bot.send_message(chat_id, f"✅ Kino va video muvaffaqiyatli saqlandi!\n\n🎬 Nomi: {title}\n🔢 Kodi: `{code}`", parse_mode="Markdown", reply_markup=main_menu())
            else:
                bot.send_message(chat_id, "⚠️ Xato format! Izohga quyidagicha yozing:\n`Kod | Nomi | Janri | Tavsifi`", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(chat_id, "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring.")
    else:
        bot.send_message(chat_id, "⚠️ Avval menyudan **'📥 Kino yuklash'** tugmasini bosing, keyin videoni yuboring.", reply_markup=main_menu())

print("Bot ishga tushdi...")
bot.infinity_polling()


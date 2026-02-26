import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telebot import types

# --- Налаштування Google Sheets ---
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open('Таблиця клієнтів').sheet1

# --- Налаштування Telegram бота ---
BOT_TOKEN = '8645465791:AAEEWdiTcrlavoxQ01Z3p2YJuBfh_S364ZI'
bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

# Функція для встановлення кнопок меню (біля поля вводу)
def set_main_menu():
    bot.set_my_commands([
        types.BotCommand("start", "Додати нового клієнта"),
        types.BotCommand("help", "Як користуватися"),
        types.BotCommand("table", "Посилання на таблицю"),
        types.BotCommand("cancel", "Скасувати введення")
    ])

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    set_main_menu()
    chat_id = message.chat.id
    bot.send_message(chat_id, "🚀 **Починаємо запис.**\nБудь ласка, введіть ім'я клієнта:", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_name_step)

# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "❓ **Як працювати з ботом:**\n\n"
        "1. Натисніть /start\n"
        "2. Напишіть ПІБ клієнта\n"
        "3. Напишіть номер телефону\n"
        "4. Бот автоматично занесе це в Google Таблицю."
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')


# Команда /table
@bot.message_handler(commands=['table'])
def send_table_link(message):
    try:
        
        table_url = f"https://docs.google.com/spreadsheets/d/{sheet.spreadsheet.id}"
        
        
        text = f"🔗 <b>Ваша база клієнтів:</b>\n{table_url}"
        
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Відкрити таблицю 📊", url=table_url)
        markup.add(btn)
        
        bot.send_message(
            message.chat.id, 
            text, 
            parse_mode='HTML', 
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Не вдалося отримати посилання.")
        print(f"Помилка: {e}")


@bot.message_handler(commands=['cancel'])
def cancel(message):
    user_data.pop(message.chat.id, None)
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.send_message(message.chat.id, "❌ Введення скасовано.")

def process_name_step(message):
    if message.text.startswith('/'): return 
    try:
        chat_id = message.chat.id
        user_data[chat_id] = {'name': message.text}
        bot.send_message(chat_id, f"Ок, записав: {message.text}.\nТепер введіть номер телефону:")
        bot.register_next_step_handler(message, process_phone_step)
    except Exception:
        bot.reply_to(message, "Помилка. Спробуйте /start ще раз.")

def process_phone_step(message):
    if message.text.startswith('/'): return
    try:
        chat_id = message.chat.id
        phone = message.text
        name = user_data[chat_id]['name']

        sheet.append_row([name, phone])
        bot.send_message(chat_id, "✅ Дані успішно додано!")
        del user_data[chat_id]
    except Exception as e:
        bot.reply_to(message, "⚠️ Помилка збереження.")
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Бот запущений (Furchik edition)...")
    set_main_menu()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
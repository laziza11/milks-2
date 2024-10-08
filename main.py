#здесь я продолжила бот с предыдущего дз
import telebot
import os
import sqlite3

TOKEN = os.getenv('YOUR_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

user_data = {}
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    '''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, name TEXT, phone TEXT, language TEXT)''')
conn.commit()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Русский", "O'zbekcha")
    bot.reply_to(message, "Привет! Пожалуйста, выберите ваш язык.", reply_markup=markup)
    user_data[message.from_user.id] = {}


@bot.message_handler(func=lambda message: message.text in ["Русский", "O'zbekcha"])
def set_language(message):
    user_data[message.from_user.id]['language'] = message.text
    bot.reply_to(message, "Введите ваше имя.")


@bot.message_handler(
    func=lambda message: message.from_user.id in user_data and 'name' not in user_data[message.from_user.id])
def set_name(message):
    user_data[message.from_user.id]['name'] = message.text
    bot.reply_to(message, "Спасибо! Теперь отправьте мне свой номер телефона.",
                 reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                     telebot.types.KeyboardButton("Отправить номер", request_contact=True)))


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    user_data[message.from_user.id]['phone'] = message.contact.phone_number
    bot.reply_to(message, "Ваш номер получен. Теперь отправьте вашу локацию.",
                 reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                     telebot.types.KeyboardButton("Отправить локацию", request_location=True)))


@bot.message_handler(content_types=['location'])
def handle_location(message):
    name = user_data[message.from_user.id]['name']
    phone = user_data[message.from_user.id]['phone']
    language = user_data[message.from_user.id]['language']
    cursor.execute("INSERT INTO users (user_id, name, phone, language) VALUES (?, ?, ?, ?)",
                   (message.from_user.id, name, phone, language))
    conn.commit()
    bot.reply_to(message, f"Спасибо, {name}! Ваши данные сохранены. Приятного использования бота!")


try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()

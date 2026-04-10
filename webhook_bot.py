from flask import Flask, request
import telebot
import os

BOT_TOKEN = '8671923612:AAHXhf--OplXIcEkKC7ibvW5KMwKZyVcZqo'
# Укажи свой домен на Beget, например: https://diesel.ru
WEBHOOK_URL = 'https://v98928j7.beget.tech/webhook'

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)


@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name or 'Клиент'
    bot.send_message(message.chat.id,
        f"✅ Здравствуйте, {name}!\n\n"
        "Ваша заявка в автомастерскую *Дизель* принята. 🔧\n"
        "Мы свяжемся с вами в ближайшее время для подтверждения записи.\n\n"
        "📞 Телефон: +7 000 000-00-00\n"
        "🕐 Режим работы: Пн–Сб 09:00–19:00",
        parse_mode='Markdown'
    )


@bot.message_handler(func=lambda m: True)
def any_message(message):
    bot.send_message(message.chat.id,
        "Для записи на обслуживание воспользуйтесь нашим сайтом.\n"
        "По вопросам звоните: 📞 +7 000 000-00-00"
    )


# Telegram шлёт сюда все обновления
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return 'ok', 200


# Установка webhook (открыть один раз в браузере)
@app.route('/set_webhook')
def set_webhook():
    bot.remove_webhook()
    result = bot.set_webhook(url=WEBHOOK_URL)
    if result:
        return '✅ Webhook установлен: ' + WEBHOOK_URL
    else:
        return '❌ Ошибка установки webhook'


# Проверка что сервер работает
@app.route('/')
def index():
    return '✅ Бот Дизель работает!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
import telebot

BOT_TOKEN = '8671923612:AAHXhf--OplXIcEkKC7ibvW5KMwKZyVcZqo'
WEBHOOK_URL = 'https://diesel-bot.onrender.com/webhook'

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Хранилище заявок: { 'username': { данные заявки } }
bookings = {}


# ── Сайт шлёт сюда заявку ─────────────────────────────────────────────────
@app.route('/booking', methods=['POST'])
def receive_booking():
    data = request.get_json()
    if not data:
        return jsonify({'ok': False, 'error': 'no data'}), 400

    tg = data.get('tg', '').replace('@', '').lower()
    if tg:
        bookings[tg] = data

    return jsonify({'ok': True}), 200


# ── Telegram webhook ───────────────────────────────────────────────────────
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json())
    bot.process_new_updates([update])
    return 'ok', 200


# ── Обработка /start ───────────────────────────────────────────────────────
@bot.message_handler(commands=['start'])
def start(message):
    username = (message.from_user.username or '').lower()
    name = message.from_user.first_name or 'Клиент'

    if username and username in bookings:
        b = bookings[username]
        text = (
            'Здравствуйте, ' + name + '!\n\n'
            'Ваша заявка в автомастерскую Дизель принята. \U0001f527\n\n'
            'Детали записи:\n'
            'Услуга: ' + b.get('service', '-') + '\n'
            'Автомобиль: ' + b.get('car', '-') + ((' (' + b.get('year') + ')') if b.get('year') else '') + '\n'
        )
        if b.get('date'):
            text += 'Дата: ' + b.get('date') + '\n'
        if b.get('time'):
            text += 'Время: ' + b.get('time') + '\n'
        if b.get('comment'):
            text += 'Комментарий: ' + b.get('comment') + '\n'
        text += '\nМы свяжемся с вами для подтверждения.\nТелефон: +7 000 000-00-00'
        del bookings[username]
    else:
        text = (
            'Здравствуйте, ' + name + '!\n\n'
            'Это бот автомастерской Дизель.\n'
            'Для записи воспользуйтесь нашим сайтом.\n\n'
            'Телефон: +7 000 000-00-00\n'
            'Пн-Сб: 09:00-19:00'
        )

    bot.send_message(message.chat.id, text)


@bot.message_handler(func=lambda m: True)
def any_message(message):
    bot.send_message(message.chat.id,
        'Для записи воспользуйтесь нашим сайтом.\nПо вопросам звоните: +7 000 000-00-00'
    )


@app.route('/set_webhook')
def set_webhook():
    bot.remove_webhook()
    result = bot.set_webhook(url=WEBHOOK_URL)
    if result:
        return 'Webhook установлен: ' + WEBHOOK_URL
    return 'Ошибка установки webhook'


@app.route('/')
def index():
    return 'Бот Дизель работает!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

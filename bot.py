import sys
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import config
import database as db
from handlers import start, button_handler, add_service_text
import asyncio

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)

app = Flask(__name__)

# Инициализация приложения Telegram
application = Application.builder().token(config.TOKEN).build()

# Регистрируем обработчики
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_service_text))

@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимает обновления от Telegram"""
    try:
        # Получаем данные из запроса
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, application.bot)
        
        # Обрабатываем обновление асинхронно
        asyncio.run(application.process_update(update))
        
        return 'ok', 200
    except Exception as e:
        logging.error(f"Ошибка в вебхуке: {e}")
        return 'error', 500

@app.route('/')
def index():
    """Проверка, что бот работает"""
    return '✅ Бот фитнес-тренера работает!', 200

@app.route('/set_webhook')
def set_webhook():
    """Устанавливает вебхук (вызови один раз после деплоя)"""
    import requests
    webhook_url = f"https://{request.host}/webhook"
    url = f"https://api.telegram.org/bot{config.TOKEN}/setWebhook?url={webhook_url}"
    
    response = requests.get(url)
    if response.json().get('ok'):
        return f"✅ Вебхук установлен: {webhook_url}", 200
    else:
        return f"❌ Ошибка: {response.json()}", 400

@app.route('/remove_webhook')
def remove_webhook():
    """Удаляет вебхук (если нужно отладить)"""
    import requests
    url = f"https://api.telegram.org/bot{config.TOKEN}/setWebhook?url="
    response = requests.get(url)
    return f"Вебхук удалён: {response.json()}", 200

# Инициализация базы данных при запуске
db.init_db()
print("✅ База данных инициализирована")
print("🚀 Бот запущен на PythonAnywhere")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
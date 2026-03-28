import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import config
import database as db
from handlers import start, button_handler, add_service_text
from scheduler import send_reminders

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    # Инициализация базы данных
    db.init_db()
    
    # Создание приложения
    app = Application.builder().token(config.TOKEN).build()
    
    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_service_text))
    
    # Напоминания каждые 30 минут
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(send_reminders, interval=1800, first=10)
    
    print("✅ Бот фитнес-тренера запущен!")
    
    # Запуск бота
    app.run_polling()

if __name__ == "__main__":
    main()

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8701439086:AAHzvP8D0Q8sfVWc9kjerQfjgGewniB4ggI"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Бот работает! Версия без базы данных.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("✅ Бот запущен (минимальная версия)")
    app.run_polling()

if __name__ == "__main__":
    main()

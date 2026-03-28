import logging
from telegram.ext import ContextTypes
import database as db

logger = logging.getLogger(__name__)

async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет напоминания за 24 часа до тренировки"""
    appointments = db.get_appointments_for_reminder(24)
    
    if not appointments:
        return
    
    for apt in appointments:
        user_id, datetime_str, service_name = apt
        date_part = datetime_str.split()[0]
        time_part = datetime_str.split()[1][:5] if len(datetime_str.split()) > 1 else "по согласованию"
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🔔 *Напоминание!*\n\n"
                     f"Завтра {date_part} в {time_part} у вас {service_name}.\n\n"
                     f"Готовьтесь к тренировке! 💪",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Ошибка напоминания {user_id}: {e}")
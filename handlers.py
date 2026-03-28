import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import config
import database as db
import keyboards as kb

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_client(user.id, user.username, user.full_name)
    
    is_admin = (user.id == config.ADMIN_ID)
    
    # Вставь сюда свой file_id
    photo_file_id = "AgACAgIAAxkBAAMLacacHAKCVJnDMqC64PiI8tMlyT0AArQUaxtLuTlK5ghsTLKt2lEBAAMCAAN4AAM6BA"  # замени на свой
    
    await update.message.reply_photo(
        photo=photo_file_id,
        caption=(
            f"🏆 *Привет, {user.first_name}!*\n\n"
            "Меня зовут Алексей, я твой онлайн-наставник.\n"
            "Я работаю с атлетами, которые хотят:\n"
            "• Чёткую структуру тренировок\n"
            "• Прогресс без травм\n"
            "• Результат, а не просто «потеть в зале»\n\n"
            "Если ты готов двигаться к цели с поддержкой профессионала — ты по адресу.\n\n"
            "👇 *Выбери, что нужно:*"
        ),
        parse_mode="Markdown",
        reply_markup=kb.main_menu(is_admin)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "services":
        await show_services(query)
    elif data == "book":
        await show_services_for_booking(query, context)
    elif data == "my_appointments":
        await show_my_appointments(query)
    elif data == "contacts":
        await show_contacts(query)
    elif data == "back":
        user_id = query.from_user.id
        is_admin = (user_id == config.ADMIN_ID)
        await query.message.reply_text(
            "Главное меню:",
            reply_markup=kb.main_menu(is_admin)
        )
    elif data == "admin_panel":
        await show_admin_panel(query)
    elif data == "admin_all_appointments":
        await show_all_appointments(query)
    elif data == "admin_add_service":
        await show_add_service(query, context)
    elif data == "admin_stats":
        await show_stats(query)
    elif data.startswith("service_"):
        service_id = int(data.split("_")[1])
        context.user_data["booking_service"] = service_id
        await show_times(query, context)
    elif data.startswith("confirm_"):
        parts = data.split("_")
        service_id = int(parts[1])
        datetime_str = parts[2]
        await save_appointment(query, service_id, datetime_str, context)
    elif data.startswith("cancel_"):
        apt_id = int(data.split("_")[1])
        await cancel_appointment(query, apt_id)

async def show_services(query):
    services = db.get_services()
    text = "💪 *Программы тренировок:*\n\n"
    for s in services:
        price_text = f"{s[2]}₽" if s[2] > 0 else "Бесплатно"
        text += f"• {s[1]} — {price_text}\n"
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb.back_button())

async def show_services_for_booking(query, context):
    services = db.get_services()
    await query.message.reply_text("Выберите программу:", reply_markup=kb.services_menu(services))

async def show_times(query, context):
    """Для услуг без привязки ко времени — сразу подтверждение"""
    service_id = context.user_data.get("booking_service")
    date_str = datetime.now().strftime("%Y-%m-%d")
    datetime_str = f"{date_str} 00:00"
    await show_confirm(query, service_id, datetime_str)

async def show_confirm(query, service_id, datetime_str):
    service = db.get_service_by_id(service_id)
    if not service:
        await query.message.reply_text("Ошибка.", reply_markup=kb.main_menu())
        return
    
    price_text = f"{service[2]}₽" if service[2] > 0 else "Бесплатно"
    
    await query.message.reply_text(
        f"📝 *Подтвердите заказ:*\n\n"
        f"Услуга: {service[1]}\n"
        f"Стоимость: {price_text}\n\n"
        f"{'После оплаты я пришлю программу.' if service[2] > 0 else ''}\n\n"
        f"Подтверждаете?",
        parse_mode="Markdown",
        reply_markup=kb.confirm_menu(service_id, datetime_str)
    )

async def save_appointment(query, service_id, datetime_str, context):
    user_id = query.from_user.id
    db.add_appointment(user_id, service_id, datetime_str)
    service = db.get_service_by_id(service_id)
    
    # Получаем данные клиента
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()
    c.execute("SELECT full_name, username, phone FROM clients WHERE user_id = ?", (user_id,))
    client = c.fetchone()
    conn.close()
    
    client_name = client[0] if client and client[0] else "Неизвестно"
    client_username = client[1] if client and client[1] else "нет username"
    client_phone = client[2] if client and client[2] else "не указан"
    
    # Отправляем уведомление админу
    try:
        await context.bot.send_message(
            chat_id=config.ADMIN_ID,
            text=f"🆕 *Новый заказ!*\n\n"
                 f"👤 Клиент: {client_name}\n"
                 f"📱 Username: @{client_username}\n"
                 f"📞 Телефон: {client_phone}\n"
                 f"💪 Услуга: {service[1]}\n"
                 f"💰 Стоимость: {service[2]}₽\n\n"
                 f"Свяжитесь с клиентом! 🚀",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Ошибка отправки уведомления админу: {e}")
    
    # Ответ клиенту
    await query.message.reply_text(
        f"✅ *Отлично!*\n\n"
        f"Вы выбрали: {service[1]}\n"
        f"Стоимость: {service[2]}₽\n\n"
        f"🎯 *Что дальше?*\n"
        f"1. Я свяжусь с вами в ближайшее время\n"
        f"2. Оплата — после обсуждения деталей\n"
        f"3. Начнём работу!\n\n"
        f"Жду сообщения! 💪",
        parse_mode="Markdown",
        reply_markup=kb.main_menu()
    )

async def show_my_appointments(query):
    user_id = query.from_user.id
    appointments = db.get_appointments_by_user(user_id)
    if not appointments:
        await query.message.reply_text("У вас нет активных заказов.", reply_markup=kb.main_menu())
        return
    text = "📅 *Ваши заказы:*\n\n"
    for apt in appointments:
        text += f"• {apt[1]}\n"
    text += "\nНажмите на заказ, чтобы отменить."
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb.appointment_menu(appointments))

async def cancel_appointment(query, appointment_id):
    user_id = query.from_user.id
    db.cancel_appointment(appointment_id, user_id)
    await query.message.reply_text("❌ Заказ отменён.", reply_markup=kb.main_menu())

async def show_contacts(query):
    text = "📞 *Контакты тренера:*\n\n"
    text += "📍 Онлайн-тренировки в любом месте\n"
    text += "📱 Telegram: @LX_570sss\n"
    text += "💬 Instagram: @xnxwix\n"
    text += "📞 Телефон: +7 (965) 705-74-78\n\n"
    text += "По всем вопросам пишите тренеру!"
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb.back_button())

async def show_admin_panel(query):
    if query.from_user.id != config.ADMIN_ID:
        await query.message.reply_text("У вас нет доступа к админ-панели.")
        return
    await query.message.reply_text(
        "🔧 *Админ-панель*\n\nВыберите действие:",
        parse_mode="Markdown",
        reply_markup=kb.admin_panel()
    )

async def show_all_appointments(query):
    if query.from_user.id != config.ADMIN_ID:
        await query.message.reply_text("Нет доступа.")
        return
    
    appointments = db.get_all_appointments()
    
    if not appointments:
        await query.message.reply_text("📭 Нет заказов.", reply_markup=kb.back_button())
        return
    
    text = "📋 *Все заказы:*\n\n"
    for apt in appointments:
        apt_id, datetime_str, service_name, client_name, username, phone = apt
        text += f"• {service_name}\n"
        text += f"  👤 {client_name} (@{username or 'нет username'})"
        if phone:
            text += f" | 📞 {phone}"
        text += "\n\n"
    
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb.back_button())

async def show_add_service(query, context):
    if query.from_user.id != config.ADMIN_ID:
        await query.message.reply_text("Нет доступа.")
        return
    
    context.user_data["adding_service"] = True
    await query.message.reply_text(
        "➕ *Добавление программы*\n\n"
        "Введите название, цену и длительность в формате:\n"
        "`Название|цена|длительность`\n\n"
        "Например:\n"
        "• `5 тренировок|6000|0` (без времени)\n"
        "• `Консультация|1500|45` (45 минут)\n\n"
        "Или нажмите Назад для отмены.",
        parse_mode="Markdown",
        reply_markup=kb.back_button()
    )

async def add_service_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("adding_service"):
        return
    
    if update.effective_user.id != config.ADMIN_ID:
        return
    
    text = update.message.text
    
    try:
        parts = text.split("|")
        if len(parts) != 3:
            raise ValueError("Неверный формат")
        
        name = parts[0].strip()
        price = int(parts[1].strip())
        duration = int(parts[2].strip())
        
        conn = sqlite3.connect("fitness.db")
        c = conn.cursor()
        c.execute("INSERT INTO services (name, price, duration) VALUES (?, ?, ?)", (name, price, duration))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ Программа \"{name}\" ({price}₽, {duration} мин) добавлена!",
            reply_markup=kb.admin_panel()
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Ошибка: {e}\n\n"
            "Используйте формат: Название|цена|длительность\n"
            "Например: 5 тренировок|6000|0",
            reply_markup=kb.back_button()
        )
    
    context.user_data.pop("adding_service", None)

async def show_stats(query):
    if query.from_user.id != config.ADMIN_ID:
        await query.message.reply_text("Нет доступа.")
        return
    
    conn = sqlite3.connect("fitness.db")
    c = conn.cursor()
    
    # Всего клиентов
    c.execute("SELECT COUNT(*) FROM clients")
    total_clients = c.fetchone()[0]
    
    # Активных заказов
    c.execute("SELECT COUNT(*) FROM appointments WHERE datetime > datetime('now') AND status != 'cancelled'")
    active_appointments = c.fetchone()[0]
    
    # Популярная программа
    c.execute('''
        SELECT s.name, COUNT(*) FROM appointments a
        JOIN services s ON a.service_id = s.id
        WHERE a.status != 'cancelled'
        GROUP BY s.name
        ORDER BY COUNT(*) DESC
        LIMIT 1
    ''')
    popular = c.fetchone()
    popular_text = f"{popular[0]} ({popular[1]} заказов)" if popular else "нет данных"
    
    conn.close()
    
    text = "📊 *Статистика:*\n\n"
    text += f"👥 Всего клиентов: {total_clients}\n"
    text += f"📅 Активных заказов: {active_appointments}\n"
    text += f"🔥 Популярная программа: {popular_text}\n"
    
    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb.back_button())

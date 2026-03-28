from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu(is_admin=False):
    keyboard = [
        [InlineKeyboardButton("💪 Услуги и цены", callback_data="services")],
        [InlineKeyboardButton("📅 Выбрать услугу", callback_data="book")],
        [InlineKeyboardButton("📋 Мои тренировки", callback_data="my_appointments")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")]
    ]
    # Кнопка админ-панели показывается только админу
    if is_admin:
        keyboard.append([InlineKeyboardButton("🔧 Админ-панель", callback_data="admin_panel")])
    return InlineKeyboardMarkup(keyboard)
    

def services_menu(services):
    keyboard = []
    for s in services:
        price_text = f"{s[2]}₽" if s[2] > 0 else "Бесплатно"
        keyboard.append([InlineKeyboardButton(f"{s[1]} — {price_text}", callback_data=f"service_{s[0]}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def date_menu(dates):
    keyboard = [[InlineKeyboardButton(d, callback_data=f"date_{d}")] for d in dates]
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def time_menu(times, service_id, date_str):
    keyboard = []
    for t in times:
        keyboard.append([InlineKeyboardButton(t, callback_data=f"time_{service_id}_{date_str}_{t}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def confirm_menu(service_id, datetime_str):
    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_{service_id}_{datetime_str}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def appointment_menu(appointments):
    if not appointments:
        return None
    keyboard = []
    for apt in appointments:
        apt_id, name, dt, status = apt
        date_part = dt.split()[0]
        time_part = dt.split()[1][:5]
        keyboard.append([InlineKeyboardButton(f"{date_part} {time_part} — {name}", callback_data=f"cancel_{apt_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back")])
    return InlineKeyboardMarkup(keyboard)

def admin_panel():
    keyboard = [
        [InlineKeyboardButton("📋 Все записи", callback_data="admin_all_appointments")],
        [InlineKeyboardButton("➕ Добавить программу", callback_data="admin_add_service")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back")]])
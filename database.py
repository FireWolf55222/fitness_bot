import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'fitness.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            duration INTEGER DEFAULT 60
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            datetime TEXT NOT NULL,
            status TEXT DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES clients (user_id),
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
    ''')
    
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            ("🎯 Консультация (разбор целей, анализ)", 1500, 45),
            ("📋 Программа тренировок (индивидуальная)", 2500, 0),
            ("🔥 Онлайн-ведение (месяц поддержки)", 7000, 0),
            ("💪 Онлайн-ведение (3 месяца)", 19000, 0),
        ]
        c.executemany("INSERT INTO services (name, price, duration) VALUES (?, ?, ?)", services)
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def add_client(user_id, username, full_name, phone=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO clients (user_id, username, full_name, phone)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, full_name, phone))
    conn.commit()
    conn.close()

def get_services():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, price, duration FROM services")
    services = c.fetchall()
    conn.close()
    return services

def get_service_by_id(service_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name, price, duration FROM services WHERE id = ?", (service_id,))
    service = c.fetchone()
    conn.close()
    return service

def add_appointment(user_id, service_id, datetime_str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO appointments (user_id, service_id, datetime, status)
        VALUES (?, ?, ?, 'confirmed')
    ''', (user_id, service_id, datetime_str))
    conn.commit()
    conn.close()

def get_appointments_by_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT a.id, s.name, a.datetime, a.status
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        WHERE a.user_id = ? AND a.status != 'cancelled'
        ORDER BY a.datetime DESC
    ''', (user_id,))
    appointments = c.fetchall()
    conn.close()
    return appointments

def get_all_appointments():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT a.id, a.datetime, s.name, c.full_name, c.username, c.phone
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        JOIN clients c ON a.user_id = c.user_id
        WHERE a.status != 'cancelled'
        ORDER BY a.datetime DESC
    ''')
    appointments = c.fetchall()
    conn.close()
    return appointments

def cancel_appointment(appointment_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE appointments SET status = 'cancelled'
        WHERE id = ? AND user_id = ?
    ''', (appointment_id, user_id))
    conn.commit()
    conn.close()

def get_appointments_for_reminder(hours_before=24):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT a.user_id, a.datetime, s.name
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        WHERE datetime(a.datetime) BETWEEN datetime('now', '+' || ? || ' hours') 
                                        AND datetime('now', '+' || ? || ' hours', '+1 hour')
        AND a.status = 'confirmed'
    ''', (hours_before, hours_before))
    appointments = c.fetchall()
    conn.close()
    return appointments
# Добавь сюда остальные функции (они такие же, как были)

# Остальные функции оставляем без изменений

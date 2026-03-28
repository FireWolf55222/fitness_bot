import sqlite3
from datetime import datetime, timedelta

# База данных будет в папке с приложением (сохраняется между перезапусками)
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

# Добавь сюда остальные функции (они такие же, как были)

# Остальные функции оставляем без изменений

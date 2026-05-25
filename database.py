import sqlite3

DB_NAME = "portfolio_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Добавляем колонку language, по дефолту ставим 'ukr'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            language TEXT DEFAULT 'ukr'
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Используем INSERT OR IGNORE, чтобы не перезаписывать язык, если юзер уже есть
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, language) 
        VALUES (?, ?, 'ukr')
    """, (user_id, username))
    conn.commit()
    conn.close()

def get_user_language(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.field_with_name if cursor.description else cursor.fetchone()
    conn.close()
    return result[0] if result else "ukr"

def set_user_language(user_id, lang):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users
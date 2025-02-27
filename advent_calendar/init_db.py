import sqlite3
import os
from werkzeug.security import generate_password_hash

def init_db():
    if os.path.exists("project.db"):
        os.remove("project.db")

    conn = sqlite3.connect('project.db')
    cur = conn.cursor()

    # Create users table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        account_password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create user_settings table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS user_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        unlock_password TEXT NOT NULL DEFAULT 'cowboy',
        star_password TEXT NOT NULL DEFAULT 'Spy',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Create calendar_boxes table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS calendar_boxes (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        user_id INTEGER NOT NULL,
        box_number INTEGER NOT NULL,
        image_url TEXT,
        image_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Insert admin user with fixed password 'pp'
    admin_password = generate_password_hash('pp')
    cur.execute('INSERT INTO users (username, account_password_hash) VALUES (?, ?)',
                ('admin', admin_password))

    admin_id = cur.lastrowid

    # Set default passwords for admin
    cur.execute('''
    INSERT INTO user_settings (user_id, unlock_password, star_password)
    VALUES (?, 'cowboy', 'Spy')
    ''', (admin_id,))

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
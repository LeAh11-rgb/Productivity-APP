# Manages SQLite database connection 

import sqlite3
import os
from flask import g

def get_db(app = None):
    if 'db' not in g:
        from flask import current_app
        dp_path = current_app.config['DATABASE_PATH']

        g.db = sqlite3.connect(
            dp_path, 
            detect_types = sqlite3.PARSE_DECLTYPES
        )

        g.db.row_factory = sqlite3.Row

    return g.db

def close_db (app = None):
    db = g.pop ('db', None)
    if db is not None:
        db.close()


def init_db(app):
    db_path = app.config['DATABASE_PATH']

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
        -- Users table: stores account information
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            email       TEXT UNIQUE NOT NULL,
            username    TEXT NOT NULL,
            password    TEXT NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Categories: user-defined labels for tasks (e.g., "Work", "Personal")
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT NOT NULL,
            color       TEXT DEFAULT '#6366f1',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        -- Tasks: the core data of the app
        CREATE TABLE IF NOT EXISTS tasks (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            category_id   INTEGER,
            title         TEXT NOT NULL,
            description   TEXT,
            due_date      TEXT,
            due_time      TEXT,
            priority      TEXT DEFAULT 'medium',
            is_complete   INTEGER DEFAULT 0,
            completed_at  DATETIME,
            reminder_at   DATETIME,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
        );
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

    app.teardown_appcontext(close_db)


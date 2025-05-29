import sqlite3
import hashlib

DB_NAME = 'users.db'

def create_user_table():
    """Create the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Add a new user with hashed password to the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username already exists
        return False
    finally:
        conn.close()

def verify_user(username, password):
    """Verify if username exists and password matches."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        stored_password = result[0]
        return stored_password == hash_password(password)
    else:
        return False

def get_users():
    """Return list of all usernames."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT username FROM users')
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def update_password(username, new_password):
    """Update password for a given username."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE users SET password = ? WHERE username = ?', (hash_password(new_password), username))
    conn.commit()
    conn.close()

import sqlite3

def init_db():
    conn = sqlite3.connect('atm.db')
    c = conn.cursor()

    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no TEXT UNIQUE NOT NULL,
            pin TEXT NOT NULL,
            name TEXT NOT NULL,
            balance REAL DEFAULT 0
        )
    ''')

    # Transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_no TEXT,
            type TEXT,
            amount REAL,
            balance_after REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Demo user
    c.execute("SELECT * FROM users WHERE account_no = '1234567890'")
    if not c.fetchone():
        c.execute("INSERT INTO users (account_no, pin, name, balance) VALUES (?, ?, ?, ?)",
                  ('1234567890', '1234', 'Demo User', 50000.0))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
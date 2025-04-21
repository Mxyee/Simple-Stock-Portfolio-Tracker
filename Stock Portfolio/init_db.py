import sqlite3

conn = sqlite3.connect('portfolio.db')
c = conn.cursor()

# Drop the table if it already exists
c.execute('DROP TABLE IF EXISTS transactions')

# Recreate the table
c.execute('''
    CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        price REAL NOT NULL,
        type TEXT CHECK(type IN('buy','sell')) NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print("✅ Database and table reset")

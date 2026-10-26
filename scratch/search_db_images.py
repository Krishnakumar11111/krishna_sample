import sqlite3
from pathlib import Path

BASE_DIR = Path('.')
conn = sqlite3.connect(BASE_DIR / 'db.sqlite3')
cur = conn.cursor()

print("Searching DB for 'student.png'...")
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cur.fetchall()]

for t in tables:
    cur.execute(f"PRAGMA table_info({t});")
    cols = [r[1] for r in cur.fetchall()]
    text_cols = [r[1] for r in cur.fetchall() if 'CHAR' in str(r[2]).upper() or 'TEXT' in str(r[2]).upper()]
    for col in cols:
        try:
            cur.execute(f"SELECT {col} FROM {t} WHERE {col} LIKE '%student.png%' OR {col} LIKE '%ChatGPT_Image%' OR {col} LIKE '%Screenshot_%';")
            rows = cur.fetchall()
            if rows:
                print(f"Match in table {t}, col {col}: {rows[:3]}")
        except Exception:
            pass

conn.close()

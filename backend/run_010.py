import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))

try:
    with open("migrations/010_add_analytics_indexes.sql", 'r') as f:
        sql = f.read()
    
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
        print("✅ Migration 010 applied successfully")
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    conn.close()

import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

def get_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return connection
    except Exception as e:
        print("❌ Failed to connect to PostgreSQL:", e)
        return None

# Test the connection
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("✅ Connected successfully to Supabase PostgreSQL!")
        cursor = conn.cursor()
        cursor.execute("SELECT NOW();")
        print("🕒 Current time from DB:", cursor.fetchone()[0])

        # Test pulling data from a table
        try:
            cursor.execute("SELECT * FROM product LIMIT 5;")  # Replace with your table name
            rows = cursor.fetchall()
            print("📦 Sample data from order_table:")
            for row in rows:
                print(row)
        except Exception as e:
            print("❌ Failed to fetch data:", e)

        conn.close()
    else:
        print("❌ Connection test failed.")
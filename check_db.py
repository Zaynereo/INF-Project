import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def check_mysql_connection():
    try:
        # Get database URI from environment variables
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not db_uri:
            print("Error: SQLALCHEMY_DATABASE_URI not found in .env file")
            return False
        
        # Parse the connection string
        # Format: mysql+pymysql://username:password@host/dbname
        parts = db_uri.split('://')[1].split('@')
        user_pass, host_db = parts[0], parts[1]
        username, password = user_pass.split(':')
        host, db_name = host_db.split('/')
        
        # Try to connect to MySQL
        print(f"Attempting to connect to MySQL database: {db_name} on {host}...")
        connection = pymysql.connect(
            host=host,
            user=username,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ Successfully connected to MySQL database!")
        
        # Check if tables exist
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\nFound {len(tables)} tables in the database:")
            for table in tables:
                print(f"- {list(table.values())[0]}")
        
        connection.close()
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"❌ Failed to connect to MySQL database: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure MySQL server is running")
        print("2. Verify the database credentials in .env file")
        print("3. Ensure the database 'grocerydb' exists")
        print("4. Check if the MySQL user has proper permissions")
        print("\nTo create the database, run in MySQL:")
        print("  CREATE DATABASE IF NOT EXISTS grocerydb;")
        print("  GRANT ALL PRIVILEGES ON grocerydb.* TO 'root'@'localhost';")
        print("  FLUSH PRIVILEGES;")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    check_mysql_connection()

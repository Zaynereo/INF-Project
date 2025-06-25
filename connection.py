import psycopg2
from dotenv import load_dotenv
import os
import sys
from pymongo import MongoClient

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
    
def get_mongo_connection():
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client[os.getenv("MONGO_DB_NAME")]
        return db
    
    except Exception as e:
        print("❌ Failed to connect to MongoDB:", e)
        return None
    
if __name__ == "__main__":
    db = get_mongo_connection()
    if db is not None:
        print("✅ Connected to MongoDB!")
        
        # Optional: test inserting a dummy document
        test_collection = db["Test"]
        result = test_collection.insert_one({"status": "connected", "test": True})
        print("Inserted test document with ID:", result.inserted_id)
    else:
        print("❌ Could not connect to MongoDB.")

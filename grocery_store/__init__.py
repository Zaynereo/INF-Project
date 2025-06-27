from pymongo import MongoClient
from django.conf import settings

def get_mongo_db():
    """
    Get MongoDB database connection
    """
    try:
        client = MongoClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]
        return db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None

def get_mongo_collection(collection_name):
    """
    Get a specific MongoDB collection
    """
    db = get_mongo_db()
    if db is not None:
        return db[collection_name]
    return None

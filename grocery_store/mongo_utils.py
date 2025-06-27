from pymongo import MongoClient
from django.conf import settings
from bson.objectid import ObjectId
from datetime import datetime
import json

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

# MongoDB Collections for different purposes
class MongoCollections:
    USER_ACTIVITY = 'user_activity'
    PRODUCT_ANALYTICS = 'product_analytics'
    SHOPPING_CART = 'shopping_cart'
    NOTIFICATIONS = 'notifications'
    SEARCH_LOGS = 'search_logs'

def log_user_activity(user_id, action, details=None):
    """
    Log user activity to MongoDB
    """
    collection = get_mongo_collection(MongoCollections.USER_ACTIVITY)
    if collection:
        activity = {
            'user_id': user_id,
            'action': action,
            'details': details or {},
            'timestamp': datetime.utcnow(),
            'ip_address': None  # Can be added from request
        }
        collection.insert_one(activity)
        return True
    return False

def log_product_view(product_id, user_id=None):
    """
    Log product view for analytics
    """
    collection = get_mongo_collection(MongoCollections.PRODUCT_ANALYTICS)
    if collection:
        view_data = {
            'product_id': product_id,
            'user_id': user_id,
            'view_type': 'page_view',
            'timestamp': datetime.utcnow()
        }
        collection.insert_one(view_data)
        return True
    return False

def save_shopping_cart(user_id, cart_data):
    """
    Save shopping cart to MongoDB for session persistence
    """
    collection = get_mongo_collection(MongoCollections.SHOPPING_CART)
    if collection:
        # Remove existing cart for this user
        collection.delete_many({'user_id': user_id})
        
        # Save new cart
        cart_doc = {
            'user_id': user_id,
            'cart_data': cart_data,
            'updated_at': datetime.utcnow()
        }
        collection.insert_one(cart_doc)
        return True
    return False

def get_shopping_cart(user_id):
    """
    Retrieve shopping cart from MongoDB
    """
    collection = get_mongo_collection(MongoCollections.SHOPPING_CART)
    if collection:
        cart_doc = collection.find_one({'user_id': user_id})
        if cart_doc:
            return cart_doc.get('cart_data', {})
    return {}

def log_search_query(query, user_id=None, results_count=0):
    """
    Log search queries for analytics
    """
    collection = get_mongo_collection(MongoCollections.SEARCH_LOGS)
    if collection:
        search_log = {
            'query': query,
            'user_id': user_id,
            'results_count': results_count,
            'timestamp': datetime.utcnow()
        }
        collection.insert_one(search_log)
        return True
    return False

def get_product_analytics(product_id, days=30):
    """
    Get analytics for a specific product
    """
    collection = get_mongo_collection(MongoCollections.PRODUCT_ANALYTICS)
    if collection:
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                '$match': {
                    'product_id': product_id,
                    'timestamp': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        'date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
                        'view_type': '$view_type'
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'_id.date': 1}
            }
        ]
        
        return list(collection.aggregate(pipeline))
    return []

def create_notification(user_id, title, message, notification_type='info'):
    """
    Create a notification for a user
    """
    collection = get_mongo_collection(MongoCollections.NOTIFICATIONS)
    if collection:
        notification = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'read': False,
            'created_at': datetime.utcnow()
        }
        collection.insert_one(notification)
        return True
    return False

def get_user_notifications(user_id, limit=10):
    """
    Get notifications for a user
    """
    collection = get_mongo_collection(MongoCollections.NOTIFICATIONS)
    if collection:
        notifications = collection.find(
            {'user_id': user_id}
        ).sort('created_at', -1).limit(limit)
        return list(notifications)
    return [] 
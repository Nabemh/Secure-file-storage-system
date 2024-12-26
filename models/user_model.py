from flask import current_app
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

def get_db():
    client = MongoClient(current_app.config['MONGO_URI'])
    return client['secure_file_storage']

db = get_db()
users = db['users']

def register_user(username, password):
    try:

        if users.find_one({'username': username}):
            return {"Success" : False, "Message": "User already exists."}
        hashed_password = generate_password_hash(password)
        users.insert_one({'username': username, 'password': hashed_password})
        return {"Success": True, "Message": "Registration successful."}
    except Exception as e:
        return False

def authenticate_user(username, password):
    user = users.find_one({'username' : username})

    if user is None:
        return False
    
    stored_hash = user['password']

    if check_password_hash(stored_hash, password):
        return True
    else:
        return False
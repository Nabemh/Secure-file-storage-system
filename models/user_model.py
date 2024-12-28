import ssl
from flask import current_app
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash

def get_db(app):
  mongo_uri = app.config['MONGO_URI']
  client = MongoClient(mongo_uri, server_api=ServerApi('1'))
  return client['secure_file_storage']

def register_user(db, username, password):

    users = db['users']
    try:

        if users.find_one({'username': username}):
            return {"Success" : False, "Message": "User already exists."}
        hashed_password = generate_password_hash(password)
        users.insert_one({'username': username, 'password': hashed_password})
        return {"Success": True, "Message": "Registration successful."}
    except Exception as e:
        return False

def authenticate_user(db, username, password):

    users = db['users']
    user = users.find_one({'username' : username})

    if user is None:
        return False
    
    stored_hash = user['password']

    if check_password_hash(stored_hash, password):
        return True
    else:
        return False
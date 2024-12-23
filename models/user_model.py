from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

client = MongoClient('mongodb://localhost:27017/')
db = client['file_storage']
users = db['users']

def register_user(username, password):
    if users.find_one({'username': username}):
        return False
    hashed_password = generate_password_hash(password)
    users.insert_one({'username': username, })
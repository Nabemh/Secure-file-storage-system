import datetime
from models.user_model import get_db

def get_files_collection(app):
    db = get_db(app) 
    return db['files']

def save_metadata(app, username, file_name, local_path, file_path, download_url=None):
    files_collection = get_files_collection(app)
    files_collection.insert_one({
        'username': username,
        'file_name': file_name,
        'local_path': local_path,
        'file_path': file_path,
        'download_url': download_url,
        'upload_date': datetime.datetime.utcnow()
    })

def get_metadata(app, username):
    files_collection = get_files_collection(app)
    return list(files_collection.find({'username': username}))

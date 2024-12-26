import datetime
from models.user_model import get_db

db = get_db()
files_collection = db['files']

def save_metadata(username, file_name, local_path, file_path, download_url=None):
    files_collection.insert_one({
        'username': username,
        'file_name': file_name,
        'local_path': local_path,
        'file_path': file_path,
        'download_url': download_url,
        'upload_date': datetime.utcnow()
    })

def get_metadate(username):
    return list(files_collection.find({'username' : username}))
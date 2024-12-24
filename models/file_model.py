files_collection = db['files'] # type: ignore

def save_metadata(username, file_name, file_path, s3_url):
    files_collection.insert_one({
        'username': username,
        'file_name': file_name,
        'file_path': file_path,
        's3_url': s3_url
    })

def get_metadate(username):
    return list(files_collection.find({'username' : username}))
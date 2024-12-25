from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from pymongo import MongoClient
from models.user_model import register_user, authenticate_user
from models.file_model import save_file_metadata, get_user_files
from utils.auth import User
from utils.encrypt import encrypt_file, decrypt_file
import boto3
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

#Accessing needed configurations
mongo_uri = app.config['MONGO_URI']
app.secret_key = os.urandom(24)

#initializing flask login extensions
login_manager = LoginManager()
login_manager.init_app(app)

#mongodb setup
client = MongoClient(mongo_uri)
db = client['secure_file_storage']
users_collection = db['users']
files_collection = db['files']

#routes
@app.route('/')
@login_required
def home():
    return render_template('core/index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if authenticate_user(username, password):
        user = User(username)
        login_user(user)
        return redirect(url_for('dashboard'))
    flash('Invalid credentials')
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    if register_user(username, password):
        flash('Registration successful! Proceed to login.')
    else:
        flash('User already exists. Please login.')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    files = get_user_files(current_user.id)
    return render_template('dashboard.html', files=files)

@app.route('/upload', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    file.save(f'uploads/{file.filename}')
    encrypt_file(f'uploads/{file.filename}')

    #uploading to aws s3

    s3_client.upload_file(f'uploads/{file.filename}',
                          app.config['AWS_S3_BUCKET'],
                          file.filename)
    s3_url = f"https://{app.config['AWS_S3_BUCKET']}.s3.amazonaws.com/{file.filename}"

    save_file_metadata(current_user.id, 
                       file.filename, 
                       f'uploads/{file.filename}', 
                       s3_url)
    flash('File uploaded successfully!')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
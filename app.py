from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from pymongo import MongoClient
from config import DevelopmentConfig
from models.user_model import register_user, authenticate_user
from models.file_model import save_file_metadata, get_user_files
from utils.auth import User
from utils.encrypt import encrypt_file, decrypt_file
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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

#creating a helper function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
    #checking if file is part of request
    if 'file' not in request.files:
        flash('No file added')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']

    #checking if user has a file selected
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('dashboard'))
    
    # validating file extension
    if not allowed_file(file.filename):
        flash('Invalid file type!')
        return redirect(url_for('dashboard'))
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    encrypt_file(file_path)

    save_file_metadata(
        user_id=current_user.id,
        filename=file.filename,
        local_path=file_path,
        download_url=None
    )

    flash('File uploaded!')
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
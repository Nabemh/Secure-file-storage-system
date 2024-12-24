from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models.user_model import register_user, authenticate_user
from models.file_model import save_file_metadata, get_user_files
from utils.encrypt import encrypt_file, decrypt_file
import boto3

app = Flask(__name__)
app.config.from_object('config.Config')

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
@login_required
def home():
    return render_template('core/index.html')
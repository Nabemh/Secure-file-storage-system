from datetime import time
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from config import DevelopmentConfig
from forms import LoginForm, RegistrationForm
from models.user_model import register_user, authenticate_user
from models.file_model import save_metadata, get_metadata
from utils.auth import User
from utils.encrypt import encrypt_file
import os

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from models.user_model import get_db  # Import here to avoid circular dependencies
    db = get_db(app)
    user_data = db['users'].find_one({'_id': user_id})
    if user_data:
        return User(user_data['username'])
    return None

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
#@login_required
def home():
    return render_template('/core/index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        from models.user_model import get_db  # Importing here to avoid circular dependencies
        db = get_db(app)  
        if authenticate_user(db, username, password):
            user = User(username)
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials')
        return redirect(url_for('home'))

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET' ,'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        from models.user_model import get_db  # Importing here to avoid circular dependencies
        db = get_db(app)
        result = register_user(db, username, password)
        flash(result['Message'], 'success' if result['Success'] else 'danger')
        
        if result['Success']:
            return redirect(url_for('login'))

        return redirect(url_for('register'))

    return render_template('register.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    # Initialize the message variable to None
    message = None

    # Handle file upload
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            # Generate unique file name using time()
            file_name = f"{int(time.time())}_{file.filename}"
            
            # Securely save the file in the 'files' folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            
            # Provide feedback to the user
            message = f"File uploaded successfully: {file_name}"
        else:
            message = "Invalid file type or no file selected."
    
    # Fetch files metadata (or any other data) for the dashboard
    files = get_metadata(app, current_user.id)
    
    # Render the dashboard template with the files and the message
    return render_template('dashboard.html', files=files, message=message)

@app.route('/upload', methods=['POST'])
#@login_required
def upload():
    # Initialize message variable
    message = None

    if 'file' not in request.files:
        message = 'No file added'
        return redirect(url_for('dashboard', message=message))

    file = request.files['file']
    if file.filename == '':
        message = 'No file selected'
        return redirect(url_for('dashboard', message=message))
    if not allowed_file(file.filename):
        message = 'Invalid file type!'
        return redirect(url_for('dashboard', message=message))

    # Save the file locally
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Encrypt the file (assuming encrypt_file is a defined function)
    encrypt_file(file_path)

    # Save file metadata
    save_metadata(
        app,
        username=current_user.id,  # Assuming `current_user.id` is username
        file_name=file.filename,
        local_path=file_path,
        file_path=file_path,
        download_url=None
    )

    message = 'File uploaded successfully!'
    return redirect(url_for('dashboard', message=message))


@app.route('/logout')
#@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

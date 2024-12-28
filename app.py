from datetime import time
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
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
#@login_required
def dashboard():
    current_user.id = 1

    message = None

    # Handle file upload (for normal form submit)
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            # Generate a unique file name using time()
            file_name = f"{int(time.time())}_{file.filename}"
            
            # Securely save the file in the 'files' folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            
            # Provide feedback to the user (for synchronous upload)
            message = f"File uploaded successfully: {file_name}"
        else:
            message = "Invalid file type or no file selected."
    
    # Fetch files metadata (or any other data) for the dashboard
    files = get_metadata(app, current_user.id)

    # Render the dashboard template with the files and the message
    return render_template('dashboard.html', files=files, message=message)


@app.route('/upload', methods=['POST'])
#@login_required  # You can comment this out if you want non-logged-in users to upload files
def upload():
    # Initialize message variable

    message = None

    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400

    file = request.files['file']
    
    # If filename is empty
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file selected'}), 400
    
    # If file type is not allowed
    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

    # Generate a unique file name and save the file
    file_name = f"{int(time.time())}_{file.filename}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file.save(file_path)

    # Encrypt the file (assuming encrypt_file is defined elsewhere)
    encrypt_file(file_path)

    # Save file metadata in database
    save_metadata(
        app,
        username=current_user.id,  # Assuming `current_user.id` is username
        file_name=file_name,
        local_path=file_path,
        file_path=file_path,
        download_url=None  # You can add a download URL if needed
    )

    # Return success response
    return jsonify({'status': 'success', 'filename': file_name, 'message': 'File uploaded successfully!'}), 200


@app.route('/logout', methods=['POST'])
#@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

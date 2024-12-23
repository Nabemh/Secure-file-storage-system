from flask_login import LoginManager, login_user, login_required, UserMixin

login_manager = LoginManager()

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username)

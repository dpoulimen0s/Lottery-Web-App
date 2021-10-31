# Imports
import socket
from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import logging
from flask_talisman import Talisman


# Logging
class SecurityFilter(logging.Filter):
    def filter(self, record):
        return "SECURITY" in record.getMessage()


# Logging Messages Configuration
fh = logging.FileHandler('lottery.log', 'w')
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

logger = logging.getLogger('')
logger.propagate = False
logger.addHandler(fh)

# Config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['SQLALCHEMY_ECHO'] = True
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LfFdRMcAAAAAEeOwLocqoG8LhRNZhE0TYF8MdMG"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LfFdRMcAAAAAILSgmbrJcTLnkDV5fG-xwPzyoR4"

# Initialise database
db = SQLAlchemy(app)

# Implementing Security Headers
csp = {
    'default-src': [
        '\'self\'',
        '\'unsafe-inline\'',
        'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css',
        'https://www.google.com/recaptcha/',
        'https://www.gstatic.com/recaptcha/',
        'https://www.recaptcha.google.com.com/recaptcha/'
    ]
}
talisman = Talisman(app, content_security_policy=csp)


# Functions
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Access has been prevented [%s, %s, %s, %s]', current_user.id,
                                current_user.email, current_user.role,
                                request.remote_addr)
                # Redirect the user to an unauthorised notice!
                return render_template('403.html')
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# Home Page View
@app.route('/')
def index():
    print(request.headers)
    return render_template('index.html')


# Error Page Views
@app.errorhandler(400)
def page_forbidden(error):
    return render_template('400.html'), 400


@app.errorhandler(403)
def page_not_found(error):
    return render_template('403.html'), 403


@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.errorhandler(503)
def internal_error(error):
    return render_template('503.html'), 503


# Application Initialisation
if __name__ == "__main__":
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    # Login Manager
    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    # Blueprints
    # Import blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from lottery.views import lottery_blueprint

    # Register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(lottery_blueprint)

    # App Running
    app.run(host=my_host, port=free_port, debug=True)

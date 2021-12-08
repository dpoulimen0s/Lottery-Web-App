# Imports
import base64
from datetime import datetime
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
from cryptography.fernet import Fernet
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from app import db


# Encrypt Function
def encrypt(data, draw_key):
    return Fernet(draw_key).encrypt(bytes(data, 'utf-8'))


# Decrypt Function
def decrypt(data, draw_key):
    return Fernet(draw_key).decrypt(data).decode("utf-8")


# User Class
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information.
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    pin_key = db.Column(db.String(100), nullable=False)

    # User activity information
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)

    # User information
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False, default='user')

    # Crypto key for user's lottery draws
    draw_key = db.Column(db.BLOB)

    # Define the relationship to Draw
    draws = db.relationship('Draw')

    # User Constructor
    def __init__(self, email, firstname, lastname, phone, password, pin_key, role):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.password = generate_password_hash(password)
        self.pin_key = pin_key
        self.draw_key = base64.urlsafe_b64encode(scrypt(password, str(get_random_bytes(32)), 32, N=2 ** 14, r=8, p=1))
        self.role = role
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = None


# Draw Class
class Draw(db.Model):
    __tablename__ = 'draws'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    draw = db.Column(db.String(100), nullable=False)
    played = db.Column(db.BOOLEAN, nullable=False, default=False)
    match = db.Column(db.BOOLEAN, nullable=False, default=False)
    win = db.Column(db.BOOLEAN, nullable=False)
    round = db.Column(db.Integer, nullable=False, default=0)

    # Draw Constructor
    def __init__(self, user_id, draw, win, round, draw_key):
        self.user_id = user_id
        self.draw = encrypt(draw, draw_key)
        self.played = False
        self.match = False
        self.win = win
        self.round = round

    # Decrypt Function for draw
    def view_draw(self, draw_key):
        self.draw = decrypt(self.draw, draw_key)


# Initialise database
def init_db():
    db.drop_all()
    db.create_all()
    admin = User(email='admin@email.com',
                 password='Admin1!',
                 pin_key='BFB5S34STBLZCOB22K6PPYDCMZMH46OJ',
                 firstname='Alice',
                 lastname='Jones',
                 phone='0191-123-4567',
                 role='admin')

    user1 = User(email='bob@email.com',
                 password='Pwd123456&',
                 pin_key='5NMO6KPHI5OY7SYHZJJ5K76RVNQRBYWG',
                 firstname='Bob',
                 lastname='Brown',
                 phone='0191-987-4321',
                 role='user')

    user2 = User(email='carol@email.com',
                 password='caroL$$987',
                 pin_key='NJC2Q4YVK3JPQCKBVVFFJABDAZTYJPHL',
                 firstname='Carol',
                 lastname='Smith',
                 phone='0191-456-7654',
                 role='user')

    db.session.add(admin)
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
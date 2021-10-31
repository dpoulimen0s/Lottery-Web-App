# Imports
import logging
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from app import db, requires_roles
from models import User
from users.forms import RegisterForm, LoginForm
from werkzeug.security import check_password_hash
from datetime import datetime
import pyotp

# Config
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# Views
# View registration
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # Create signup form object
    form = RegisterForm()

    # If request method is POST or form is valid
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # If this returns a user, then the email already exists in database

        # If email already exists redirect user back to signup page with error message so user can try again
        if user:
            flash('Email address already exists')
            return render_template('register.html', form=form)

        # Create a new user with the form data
        new_user = User(email=form.email.data,
                        firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        phone=form.phone.data,
                        password=form.password.data,
                        pin_key=form.pin_key.data,
                        role='user')

        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        logging.warning('SECURITY - User registration [%s, %s]', form.email.data, request.remote_addr)

        # Sends user to login page and displays a message that a user has been created.
        return redirect(url_for('users.login')), flash('The user ' + new_user.email + ' has been created!')

    # If request method is GET or form not valid re-render signup page
    return render_template('register.html', form=form)


# View user login
@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # if session attribute logins does not exist create attribute logins
    if not session.get('logins'):
        session['logins'] = 0
    # if login attempts is 3 or more create an error message
    elif session.get('logins') >= 3:
        flash('Number of incorrect logins exceeded')

    form = LoginForm()

    if form.validate_on_submit():
        # increase login attempts by 1
        session['logins'] += 1

        user = User.query.filter_by(email=form.username.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            logging.warning('SECURITY - Invalid log in attempt [%s]', request.remote_addr)
            # if no match create appropriate error message based on login attempts
            if session['logins'] == 3:
                flash('Number of incorrect logins exceeded')
            elif session['logins'] == 2:
                flash('Please check your login details and try again. 1 login attempt remaining')
            else:
                flash('Please check your login details and try again. 2 login attempts remaining')

            return render_template('login.html', form=form)

        if pyotp.TOTP(user.pin_key).verify(form.pinkey.data):

            # if user is verified reset login attempts to 0
            session['logins'] = 0

            login_user(user)

            user.last_logged_in = user.current_logged_in
            user.current_logged_in = datetime.now()
            db.session.add(user)
            db.session.commit()

            logging.warning('SECURITY - Log in [%s, %s, %s]', current_user.id, current_user.email,
                            request.remote_addr)

            # direct to role appropriate page
            if current_user.role == 'admin':
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('users.profile'))

        else:
            flash("You have supplied an invalid 2FA token! ", "danger")

    return render_template('login.html', form=form)


# View user profile
@users_blueprint.route('/profile')
@login_required
@requires_roles('user')
def profile():
    return render_template('profile.html', name=current_user.firstname)


# View user account
@users_blueprint.route('/account')
@login_required
def account():
    return render_template('account.html',
                           acc_no=current_user.id,
                           email=current_user.email,
                           firstname=current_user.firstname,
                           lastname=current_user.lastname,
                           phone=current_user.phone)


@users_blueprint.route('/logout')
@login_required
def logout():
    logging.warning('SECURITY - Log out [%s, %s, %s]', current_user.id, current_user.email, request.remote_addr)
    logout_user()
    return redirect(url_for('index'))

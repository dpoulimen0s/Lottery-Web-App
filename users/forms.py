# Imports
import re
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError


# Login Form
class LoginForm(FlaskForm):
    username = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    pinkey = StringField(validators=[Required(), Length(6, message='Length must be exactly 6 digits.')])
    recaptcha = RecaptchaField()
    submit = SubmitField()


# Function to check characters in fields.
def character_check(form, field):
    excluded_chars = "*?!'^+%&/()=}][{$#@<>"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed.")


# Register Form
class RegisterForm(FlaskForm):
    email = StringField(validators=[Required(), Email()])
    firstname = StringField(validators=[Required(), character_check])
    lastname = StringField(validators=[Required(), character_check])
    phone = StringField(validators=[Required()])

    # Function to validate the correct format of phone.
    def validate_phone(form, field):
        p = re.compile("^[0-9]{4}-[0-9]{3}-[0-9]{4}$", re.IGNORECASE)

        if len(field.data) > 13 or len(field.data) < 13 or not p.match(form.phone.data):
            raise ValidationError('Invalid phone number or not number. Must be of the form XXXX-XXX-XXXX with numbers.'
                                  ' (4 numbers - 3 numbers - 4 numbers.)')
        return

    password = PasswordField(validators=[Required(), Length(min=6, max=12, message='Password must be between 6 and 12 '
                                                                                   'characters in length.')])
    confirm_password = PasswordField(validators=[Required(), EqualTo('password', message='Both password fields must '
                                                                                         'be equal!')])
    pin_key = StringField(validators=[Required(), Length(32, message="Pin Key must be exactly 32 characters long.")])
    submit = SubmitField(validators=[Required()])

    # Function to validate the password.
    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[^\w\d])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit, 1 lowercase, 1 uppercase and 1 special "
                                  "character.")

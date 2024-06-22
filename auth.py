from flask import Blueprint, request, jsonify, redirect, url_for, render_template,make_response
from flask_wtf import FlaskForm
from flask_login import LoginManager, UserMixin, login_user, current_user
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired,Length,Email
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import app


auth_bp = Blueprint('auth', __name__, template_folder='templates')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[Length(min=4, max=150)])
    password = PasswordField('Password', validators=[])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=150)])
    mail = StringField('Mail',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class ForgotPasswordForm(FlaskForm):
    mail = StringField('Mail',validators=[DataRequired(), Email()])
    submit = SubmitField('Reset password')


@auth_bp.route('/login', methods=['GET', 'POST'])
def index():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    error=""
    form=LoginForm() 
    if form.validate_on_submit():
        user = app.User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user,remember=True)
            if form.remember.data:
                response = make_response(redirect('task'))
                response.set_cookie('username', form.username.data)
                response.set_cookie('password', form.password.data)
            return response
        else:
            error="invalid username or password"
    return render_template('login.html',form=form,error_text=error, username=username, password=password)

@auth_bp.route('/register', methods=['GET','POST'])
def register_view():
    error = " "
    form=RegisterForm()
    if form.validate_on_submit():
        username = app.User.query.filter_by(username=form.username.data).first()
        email = app.User.query.filter_by(email=form.mail.data).first()
        if username or email:
            error = 'Username or email already exists'
        else:
            password_h = generate_password_hash(form.password.data, method='pbkdf2')
            new_user = app.User(username=form.username.data, email=form.mail.data, password=password_h)
            app.db.session.add(new_user)
            app.db.session.commit()
            return redirect('login')
    return render_template('register.html',form=form, error_text=error)

@auth_bp.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    error = " "
    form=ForgotPasswordForm()
    if form.validate_on_submit():
        email = app.User.query.filter_by(email=form.mail.data).first()
        if email:
            msg = Message('Password reset', sender = '...', recipients = [form.mail.data])
            msg.body = f'this is your new password: '
        else:
            error = 'Email does not exist'
    return render_template('forgot_password.html',form=form, error_text=error)
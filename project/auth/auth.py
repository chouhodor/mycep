from flask import Blueprint, render_template, redirect, url_for, request, flash 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from flask_mail import Mail, Message
from flask_jwt_extended import jwt_required, create_access_token
from ..models import User, OAuth
from .. import db, mail
import os

auth = Blueprint('auth', __name__, template_folder='templates', static_folder='static')

@auth.route('/login')
def login():
  return render_template('login.html', hide=True) 

@auth.route('/login', methods=['POST']) 
def login_post():
  email = request.form.get('email')
  password = request.form.get('password')
  remember = True if request.form.get('remember') else False

  user = User.query.filter_by(email=email).first()

  if not user or not check_password_hash(user.password, password):
    flash('Please check your login details and try again.', 'danger')
    return redirect(url_for('auth.login'))

  login_user(user, remember=remember)

  return redirect(url_for('scheduler.index')) 

def send_email(user):
  token = user.get_reset_token()

  msg = Message()
  msg.subject = "Login System: Password Reset Request"
  msg.sender = 'username@gmail.com'
  msg.recipients = [user.email]
  msg.html = render_template('reset_pwd.html', user = user, token = token)

  mail.send(msg)

@auth.route('/reset', methods=['GET','POST'])
def reset():
  if request.method == "GET":
    return render_template('reset.html')

  if request.method == "POST":
    email = request.form.get('email')
    user = User.verify_email(email)

    if user:
      send_email(user)
      flash('An email has been sent with instructions to reset your password.', 'info')
    return redirect(url_for('auth.login')) 
  
@auth.route('/reset/<token>', methods = ['GET', 'POST'])
def reset_verified(token):
  user = User.verify_reset_token(token)

  if not user:
    flash('User not found or token has expired', 'warning')
    return redirect(url_for('auth.reset'))

  password = request.form.get('password')
  # if len(password or ()) < 8:
  #   flash('Your password needs to be at least 8 characters', 'error')     
  if password:
    hashed_password = generate_password_hash(password, method='sha256')
    user.password = hashed_password

    db.session.commit()
    flash('Your password has been updated! You are now able to log in', 'success')
    return redirect(url_for('auth.login'))
  return render_template('reset_password.html')    

@auth.route('/signup')
def signup():
  
  return render_template('signup.html', hide=True)
  
@auth.route('/signup', methods=['POST'])
def signup_post():
  username = request.form.get('username')
  email = request.form.get('email')
  password = request.form.get('password')
  passwordconfirm = request.form.get('passwordconfirm')
  team = request.form.get('team')

  user = User.query.filter_by(email = email).first() 

  if user:
    flash('Email address already exists')
    return redirect(url_for('auth.signup'))
  elif password != passwordconfirm:
    flash('Password not match!')
    return redirect(url_for('auth.signup'))
  elif team == 'Select team':
    flash('Please select team!')
    return redirect(url_for('auth.signup'))
  
  new_user = User(username = username.title(), email = email, password = generate_password_hash(password, method='sha256'), team=team)

  db.session.add(new_user)
  db.session.commit()
  flash('Signup success!', 'success')
  return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('scheduler.index'))  
from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from website import db  
from flask_login import login_user, login_required, logout_user

from . import auth
from .models import User
from website.blueprints.build.models import Connection
from website.blueprints.build.models import MyTables

# Route for login screen
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Captures login details
        email = request.form.get('email')
        password = request.form.get('password')
        # Looks for user in database
        user = User.query.filter_by(email=email).first()
        if user:
            # Checks the password hash is the same if the user exists
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                session["email"] = email
                return redirect(url_for('home.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    # loads the login page
    return render_template("auth/login.html", session=session)

# Route for logout screen
@auth.route('/logout')
@login_required
def logout():
    #logs user out and clears the session
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))

# Route for the sign-up screen
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # For new users
    if request.method == 'POST':
        # Capture user details from signin form
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # Checks user information
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 5:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Creates new user and submits to the database
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('home.home'))

    return render_template("auth/sign_up.html", session=session)



# Invisible route for seeing everything in the database
@auth.route('/view_db')
def view_db():
    return render_template("auth/view_db.html",  session=session, user_values = db.session.query(User).all(), conn_values = db.session.query(Connection).all(), table_values = db.session.query(MyTables).all())

from flask import render_template, session


from . import home

@home.route('/')
def home():
    return render_template("home.html", session=session)
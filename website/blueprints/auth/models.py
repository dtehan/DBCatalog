from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# User class captures user information in the database
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())

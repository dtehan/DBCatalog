from website import db
from sqlalchemy.sql import func

# Class for holding connection details
class Connection(db.Model):
    connection_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    connection_type = db.Column(db.String(150))
    connection_host = db.Column(db.String(150))
    connection_database = db.Column(db.String(150))
    connection_user = db.Column(db.String(150))
    connection_password = db.Column(db.String(150))
    connection_port = db.Column(db.Integer)
    connection_logmech = db.Column(db.String(10))
    connection_createDate = db.Column(db.DateTime(timezone=True), default=func.now())
    connection_updateDate = db.Column(db.Date)

# Class for holding table details
class MyTables(db.Model):
    table_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    table_database = db.Column(db.String(150))
    table_name = db.Column(db.String(150))
    table_string = db.Column(db.Text)
    table_desc = db.Column(db.Text)
    table_createDate = db.Column(db.DateTime(timezone=True), default=func.now())
    table_updateDate = db.Column(db.Date)

  
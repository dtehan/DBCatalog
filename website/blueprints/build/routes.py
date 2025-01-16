
from flask import render_template, request, flash, redirect, url_for, session, jsonify
import json
import os
from . import build
from .models import Connection
from website import db
from website.blueprints.build.database import Database
from website.blueprints.auth.models import User
from website.blueprints.build.models import MyTables
from dotenv import load_dotenv, find_dotenv


def load_env():
    _ = load_dotenv(find_dotenv('DBCatalog.env'))

# Captures the connection information into the session and into the database
@build.route('/connect', methods=['GET', 'POST'])
def connect():
    user = User.query.filter_by(email=session["email"]).first()

    if request.method == 'POST': 
        session["db_type"] = request.form.get('db_type')
        session["db_host"] = request.form.get('host')
        session["db_database"] = request.form.get('database')
        session["db_user"] = request.form.get('user')
        session["db_password"] = request.form.get('password')
        session["db_port"] = request.form.get('port')
        session["db_logmech"] = request.form.get('logmech')

        new_connection = Connection(
            user_id = user.id,
            connection_type = session["db_type"],
            connection_host = session["db_host"],
            connection_database = session["db_database"],
            connection_user = session["db_user"],
            connection_password = session["db_password"],
            connection_port = session["db_port"],
            connection_logmech = session["db_logmech"],
        )

        db.session.add(new_connection)
        db.session.commit()
        
        flash("Connection Added", category='success')
        return redirect(url_for('home.home'))
    else:
        conn = Connection.query.filter_by(user_id=user.id).first()
        if conn is not None:
            initial_values = {
                "db_type": conn.connection_type,
                "host": conn.connection_host,
                "database": conn.connection_database,
                "user": conn.connection_user,
                "password": conn.connection_password,
                "port": conn.connection_port,
                "logmech": conn.connection_logmech
            }
        else:
            initial_values = {
                "db_type": "",
                "host": "",
                "database": "",
                "user": "",
                "password": "",
                "port": "",
                "logmech": ""
            }
        return render_template("build/connect.html", session=session, initial_values = initial_values)

# Route for viewing the tables and business definitions
@build.route('/view')
def view():
    # Rendering the Tables data from the database into a table
    return render_template("build/viewtables.html",  session=session, table_values = db.session.query(MyTables).all())

@build.route('/deletetable', methods=['POST'])
def deletetable():
    table = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    print(table)
    table_id = table['table_id']
    table = MyTables.query.get(table_id)
    if table:
        database=Database()
        database.llm.embed_connect()
        database.llm.vdb_create()
        database.llm.vdb_delete(table.table_name)
        db.session.delete(table)
        db.session.commit() 
    return jsonify({})



@build.route('/definition', methods=['GET', 'POST'])
def definition():
    # triggered by the "connect" button the the definition page
    load_env()
    if request.method == 'POST': 
        return redirect(url_for("build.build"))
    else:
        return render_template("build/definition.html", session=session, LLM=os.getenv("crew_type"))
    

@build.route('/build', methods=['GET'])
def build():
    # Ensure that the connection has been defined
    if "db_type" in session:
        database=Database()
        database.connect()
        database.get_tables()
        flash("build is complete", category="success")
        return redirect(url_for('build.view'))    
    else:
        flash("Define connection.", category='warning')
        return redirect(url_for('build.definition'))
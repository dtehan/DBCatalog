from flask import render_template, session, request, redirect, url_for

from . import search
from website import db   
from website.blueprints.build.models import MyTables
from website.blueprints.build.database import Database

table_values = None
semmantic_values = None

@search.route('/searchpage', methods=['GET', 'POST'])
def searchpage():
    global table_values
    if request.method == 'POST':
        session["searchdb"] = request.form.get('searchdb', None)
        session["searchtable"] = request.form.get('searchtable', None)
        session["searchcriteria"] = request.form.get('searchcriteria', None)
        return redirect(url_for('search.searchresult'))
    else:
        return render_template("search/searchpage.html", session=session, table_values=table_values)


@search.route("/searchresult" , methods=['GET'])
def searchresult():
    global table_values
    if session["searchdb"] != '':
        table_values = MyTables.query.filter(MyTables.table_database.like(f'%{session["searchdb"]}%'))
        return redirect(url_for("search.searchpage"))
    elif session["searchtable"] != '':
        table_values = MyTables.query.filter(MyTables.table_name.like(f'%{session["searchtable"]}%'))
        return redirect(url_for("search.searchpage"))
    elif session["searchcriteria"] != '':
        table_values = MyTables.query.filter(MyTables.table_desc.like(f'%{session["searchcriteria"]}%'))
        return redirect(url_for("search.searchpage"))
    else:
        table_values = None
        return redirect(url_for("search.searchpage"))

@search.route("/semmanticsearchpage", methods=["GET", "POST"])
def semmanticsearchpage():
    global semmantic_values
    if request.method == 'POST':
        session["semmantic_query"] = request.form.get('semmantic_query', None)
        return redirect(url_for('search.semmanticresult'))
    else:
        return render_template("search/semmanticsearchpage.html", session=session, semmantic_values=semmantic_values)
    
@search.route("/semmanticresult" , methods=['GET'])
def semmanticresult():
    global semmantic_values
    semmantic_values = None
    if session["semmantic_query"] != '':
        database=Database()
        database.llm.embed_connect()
        database.llm.chat_connect()
        database.llm.vdb_create()
        database.llm.vdb_chat_graph()
        semmantic_values = database.llm.vdb_chat(session["semmantic_query"])

    return redirect(url_for("search.semmanticsearchpage"))

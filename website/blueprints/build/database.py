import sys
import markdown
from .models import MyTables
from .llmconnect import LLMConnect
from website.blueprints.auth.models import User
from website import db
from flask import session
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
)
from langchain_core.documents import Document
from website.blueprints.build.llmconnect import LLMConnect




# Database class is used to connect to the database defined in connection
class Database():

    def __init__(self):
        self.llm=LLMConnect()

    # Make a connection to the database
    def connect(self):
        self.user = User.query.filter_by(email=session["email"]).first()
        
        # Format: dialect+driver://username:password@host:port/database
        print("#################################")
        print(f"Connecting to { session['db_type'] } .........")

        # Set dialect and driver based on the database
        if session["db_type"] == "mysql":
            connstr = f"mysql+mysqlconnector://{session['db_user']}:{session['db_password']}@{session['db_host']}:{session['db_port']}/{session['db_database']}"
        elif session["db_type"] == "mssql":
            driver = 'ODBC+Driver+18+for+SQL+Server'
            connstr = f"mssql+pyodbc://{session['db_user']}:{session['db_password']}@{session['db_host']}:{session['db_port']}/{session['db_database']}?TrustServerCertificate=yes&driver={driver}"
        elif session["db_type"] == "postgresql":
            connstr = f"postgresql+psycopg2://{session['db_user']}:{session['db_password']}@{session['db_host']}:{session['db_port']}/{session['db_database']}"
        elif session["db_type"] == "db2":
            connstr = f"db2+ibm_db://{session['db_user']}:{session['db_password']}@{session['db_host']}:{session['db_port']}/{session['db_database']}"
        elif session["db_type"] == "oracle":
            connstr = f"oracle+oracledb://{session['db_user']}:{session['db_password']}@{session['db_host']}"
        elif session["db_type"] == "teradatasql":
            connstr = f"teradatasql://{session['db_user']}:{session['db_password']}@{session['db_host']}:{session['db_port']}/{session['db_database']}?logmech={session['db_logmech']}"

        try:
            self.db = SQLDatabase.from_uri(connstr)
            print(f"Connection to {session['db_type']} successful.")
        except:    # Specify in standard error any other error encountered
            print("Script Failure :", sys.exc_info()[0], file=sys.stderr)
            raise
            sys.exit()

    # get_tables will get the list of tables from the connection schema, and build the Tables information
    def get_tables(self):
        print("#################################")
        print(f"Retrieving all tables from {session['db_database']} --")

        # Gets list of tables in database schema
        try:
            #Connection to the LLM
            
            self.llm.connect()

            #set up vector db
            self.llm.chat_connect()
            self.llm.embed_connect()
            self.llm.vdb_create()

            # Existing list of tables
            existing_tables = db.session.query(MyTables.table_database, MyTables.table_name).all()

            # gets list of tables in schema
            tablesString = ListSQLDatabaseTool(db=self.db).invoke("")
            all_tables = tablesString.split(",")
            # cleans up table names into a list of strings
            for i in range(len(all_tables)):
                my_table_name = all_tables[i].strip() 
                #Check if table is already in database
                if (session["db_database"], my_table_name) in existing_tables:
                    continue

                table_string = InfoSQLDatabaseTool(db=self.db).invoke(my_table_name)
                table_desc = self.llm.get_table_description(table_string)
                table_descm = markdown.markdown(table_desc)
                # Builds table structure to commit to the database
                new_table = MyTables(
                    user_id = self.user.id,
                    table_database = session["db_database"],
                    table_name = my_table_name,
                    table_string = table_string,
                    table_desc = table_descm
                )
                db.session.add(new_table)
                db.session.commit()

                # Add to the vector DB
                doc = Document( page_content=table_desc,  metadata={'database': session["db_database"]})
                self.llm.vdb_add(doc=doc, id=my_table_name)


        except:    # Specify in standard error any other error encountered
            print("Script Failure :", sys.exc_info()[0], file=sys.stderr)
            raise
            sys.exit()

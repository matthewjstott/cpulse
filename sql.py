import os
import psycopg2
from dotenv import load_dotenv

class SqlConnect:

    def __init__(self):

        load_dotenv()
        PGDATABASE = os.environ.get("PGDATABASE")
        PGHOST = os.environ.get("PGHOST")
        PGPASSWORD = os.environ.get("PGPASSWORD")
        PGPORT = os.environ.get("PGPORT")
        PGUSER = os.environ.get("PGUSER")
        try:
            self.conn = psycopg2.connect(dbname=PGDATABASE, user=PGUSER, host=PGHOST, password=PGPASSWORD)
            print('sucessfully connected!')
        except:
            print("I am unable to connect to the database")
        self.cur = self.conn.cursor()

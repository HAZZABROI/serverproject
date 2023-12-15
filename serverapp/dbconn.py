from pymysql import connect as db_connect
import pymysql.cursors
import pymysql, os
from dotenv import load_dotenv

load_dotenv()

class DBConnection():
    hostname = os.getenv("DB_HOSTNAME")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT")

    def __enter__(self):
        self.connection = db_connect(host=self.hostname,
                                     port=int(self.port),
                                     user=self.username,
                                     password=self.password,
                                     database=self.db,
                                     cursorclass=pymysql.cursors.DictCursor)
        self.cursor = self.connection.cursor()
        return self

    def read_once(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def read_all(self, query, params):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def write_query(self, query, params):
        self.cursor.execute(query, params)
        self.connection.commit()

    def __exit__(self, type, value, traceback):
        self.connection.close()


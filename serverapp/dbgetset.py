from .dbconn import DBConnection
import json, logging

f = open('logs/config.json')
config = json.load(f)

logger = logging.getLogger(__name__)
logging.config.dictConfig(config)

def get_all_withcode(code: str) -> int:
    with DBConnection() as db:
        result = db.read_once("SELECT * FROM codes WHERE code = %s", (code, ))
    return result if result else None

def get_all_fromtests(user_id: str, test) -> dict:
    with DBConnection() as db:
        query = "SELECT * FROM tests WHERE (user_id, test) = (%s, %s)" if test else "SELECT * FROM tests WHERE user_id = %s"
        result = db.read_once(query, (user_id, test, ))
    return result if result else None

def get_all_fromclasses(user_id: str) -> str:
    with DBConnection() as db:
        result = db.read_once("SELECT name FROM classes WHERE user_id = %s", (user_id, ))
    return result

def update_tests_fromtests(user_id: str, test: str, result: str, count: str, last_date: str, name: str) -> bool:
    with DBConnection() as db:
        try:
            db.write_query("UPDATE tests SET user_id = %s, test = %s, result = %s, count = %s, last_date = %s, name = %s WHERE (test, user_id) = (%s, %s)", (user_id, test, str(result), count, last_date, name, test, user_id, ))
            return True
        except Exception as e:
            return print(e)

def insert_tests_fromtests(user_id: str, test: str, result: str, count: str, last_date: str, name: str) -> bool:
    with DBConnection() as db:
        try:
            db.write_query("INSERT INTO tests (user_id, test, result, count, last_date, name) VALUES (%s, %s, %s, %s, %s, %s)", (user_id, test, str(result), count, last_date, name, ))
            return True
        except Exception as e:
            return print(e)
        
def get_info_test(test_name: str) -> dict:
    with DBConnection() as db:
        result = db.read_once("SELECT * FROM answers WHERE name = %s", (test_name, ))
    return result if result else None

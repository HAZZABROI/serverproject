from dbconn import DBConnection
import json, logging.config

def get_user(user_id: str) -> str:
    with DBConnection() as db:
        result = db.read_once("SELECT * FROM classes WHERE user_id = %s", (user_id, ))
    return result if result else None

def insert_name(user_id: str, classs: str, name: str) -> bool:
    with DBConnection() as db:
        try:
            db.write_query("INSERT INTO classes (user_id, class, name) VALUES (%s, %s, %s)", (user_id, classs, name, ))
            return True
        except Exception as e:
            return print(e)

def insert_code(user_id: str, classs: str, name: str) -> bool:
    with DBConnection() as db:
        try:
            db.write_query("INSERT INTO classes (user_id, class, name) VALUES (%s, %s, %s)", (user_id, classs, name, ))
            return True
        except Exception as e:
            return print(e)

def select_all_from_classes(user_id: str):
    with DBConnection() as db:
        result = db.read_all("SELECT * FROM classes WHERE user_id = %s", (user_id, ))
    return result if result else None

def select_all_from_tests(res: str):
    with DBConnection() as db:
        result = db.read_all("SELECT * FROM tests WHERE user_id = %s", (res, ))
    return result if result else None

def select_all_from_classes_class(classs: str):
    with DBConnection() as db:
        result = db.read_all("SELECT * FROM classes WHERE class = %s", (classs, ))
    return result if result else None

def select_one_from_classes(user_id: str):
    with DBConnection() as db:
        result = db.read_once("SELECT * FROM classes WHERE user_id = %s", (user_id, ))
    return result if result else None

def insert_code_res(user_id: str, code: str, expire_date: str) -> bool:
    with DBConnection() as db:
        try:
            db.write_query("REPLACE INTO codes (user_id, code, expire_date) VALUES (%s, %s, %s)", (int(user_id), code, expire_date, ))
            return True
        except Exception as e:
            return e

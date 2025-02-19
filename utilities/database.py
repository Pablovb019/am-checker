import inspect
import os

from psycopg import connect
from datetime import datetime

global conn # Conexión a la base de datos

def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__

# Datos de conexión a la base de datos
def db_conn():
    global conn
    conn = connect(
        dbname= os.getenv("TFG_DB_NAME"),
        user= os.getenv("TFG_DB_USER"),
        password= os.getenv("TFG_DB_PASSWD"),
        host= os.getenv("TFG_DB_HOST"),
        port= os.getenv("TFG_DB_PORT")
    )
    return conn

def check_product(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM products WHERE id = %s)", (product_id,))
            result = cursor.fetchone()[0]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def check_reviews(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM reviews WHERE product_id = %s)", (product_id,))
            result = cursor.fetchone()[0]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def get_last_product_scan(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT last_scan FROM products WHERE id = %s", (product_id,))
            result = cursor.fetchone()[0]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def update_last_product_scan(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE products SET last_scan = %s WHERE id = %s", (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))
        conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def save_product(product_id, product_info):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO products VALUES (%s, %s, %s, %s, %s)",(product_id, product_info["name"], product_info["price"], product_info["rating"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def load_reviews(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reviews WHERE product_id = %s", (product_id,))
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def save_reviews(product_id, reviews):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            for review in reviews:
                cursor.execute("INSERT INTO reviews VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (review["id"], product_id, False, review["author"], review["rating"], review["date"], review["title"], review["text"]))
            conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def check_review(review_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM reviews WHERE id = %s)", (review_id,))
            result = cursor.fetchone()[0]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e

def delete_product(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)

        e.args = (e, function_name, exception_class)
        raise e
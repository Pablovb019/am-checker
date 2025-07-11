import inspect
import os
from datetime import datetime, timezone

from psycopg import connect

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
        dbname=os.getenv("TFG_DB_NAME"),
        user=os.getenv("TFG_DB_USER"),
        password=os.getenv("TFG_DB_PASSWD"),
        host=os.getenv("TFG_DB_HOST"),
        port=os.getenv("TFG_DB_PORT")
    )
    return conn

def check_unique_user(device_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM user_sessions WHERE user_id = %s)", (device_id,))
            result = cursor.fetchone()[0]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e

def insert_new_user(device_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO user_sessions (user_id, accessed_at) VALUES (%s, %s)", (device_id, datetime.now(timezone.utc)))
            conn.commit()
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e

def get_tracked_ids():
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM user_sessions")
            data = cursor.fetchall()
            result = set(row[0] for row in data)
        conn.close()
        return result
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e


def load_reviews(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reviews WHERE product_id = %s", (product_id,))
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in data]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e

def load_product(product_id):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row)) if row else None
        conn.close()
        return result
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e


def get_recent_products(time_threshold):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT p.*, COUNT(r.id) as review_count 
                FROM products p
                LEFT JOIN reviews r ON p.id = r.product_id
                WHERE p.last_scan >= %s
                GROUP BY p.id
                ORDER BY p.last_scan DESC
            """, (time_threshold,))

            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in data]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e

def get_site_stats():
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM site_stats")
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            result = [dict(zip(columns, row)) for row in data]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e
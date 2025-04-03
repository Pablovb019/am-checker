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

def check_predictions(product_id):
    try:
        conn = db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS(SELECT 1 FROM products WHERE id=%s AND ml_predict_avg IS NOT NULL)", (product_id,))
            result = cur.fetchone()[0]
        conn.close()
        return result > 0
    except Exception as e:
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

def update_reviews(product_id, reviews):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            for review in reviews:
                cursor.execute("""
                    UPDATE reviews
                    SET ml_predict = %s
                    WHERE product_id = %s AND id = %s
                """, (review['ml_predict'], product_id, review['id']))
            conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e

def update_product(product_id, avg_model):
    global conn
    try:
        conn = db_conn()
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE products
                SET ml_predict_avg = %s, ml_predict_date = %s
                WHERE id = %s
            """, (avg_model, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))
            conn.commit()
        conn.close()
    except Exception as e:
        conn.close()
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e
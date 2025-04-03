import inspect
import os

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
        dbname= os.getenv("TFG_DB_NAME"),
        user= os.getenv("TFG_DB_USER"),
        password= os.getenv("TFG_DB_PASSWD"),
        host= os.getenv("TFG_DB_HOST"),
        port= os.getenv("TFG_DB_PORT")
    )
    return conn

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
            cursor.execute("SELECT 1 FROM products WHERE id = %s", (product_id,))
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
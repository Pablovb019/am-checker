import cudf
import calendar
from numba import cuda
import gc
import inspect
import os

def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__

def preprocess_reviews(product_id, reviews):
    try:
        # === DATAFRAME CREATION ===
        df = cudf.DataFrame({
            'reviewText': cudf.Series([r['text'] for r in reviews]),
            'summary': cudf.Series([r['title'] for r in reviews]),
            'productRating': cudf.Series([float(r['rating']) for r in reviews]),
            'reviewTime': cudf.Series([r[str('date')] for r in reviews]),
            'asin': cudf.Series([product_id] * len(reviews)),
        })

        # === TEXT PREPROCESSING ===
        for col in ['reviewText', 'summary']:
            df[col] = df[col].str.lower().str.replace(r"[^a-z0-9'\s]", "", regex=True)

        # === LENGTH FEATURES ===
        df["reviewLength"] = df["reviewText"].str.len().astype('int16')
        df["summaryLength"] = df["summary"].str.len().astype('int16')

        # === TEMPORAL FEATURES ===
        if df['reviewTime'].str.contains(r"^\w{3},\s*\d{2}\s+\w{3}\s+\d{4}\s+\d{2}:\d{2}:\d{2}\s+GMT$").any():
            # CASE 1: "Mon, 01 Jan 2000 00:00:00 GMT"
            date_clean = df['reviewTime'].str.replace(r'^\w{3},\s*|\s*GMT$', '', regex=True)
            month_to_num = {mon: f"{num:02d}" for num, mon in enumerate(calendar.month_abbr) if num > 0}
            split_date = date_clean.str.split(" ", expand=True)

            day = split_date[0]
            month = split_date[1].map(month_to_num)
            year = split_date[2] + ' ' + split_date[3]

            reviewTime = month + '-' + day + '-' + year
        else:
            # Case 2: "01-01-2000"
            split_date = df['reviewTime'].str.split("-", expand=True)

            day = split_date[0]
            month = split_date[1]
            year = split_date[2]

            reviewTime = month + '-' + day + '-' + year + ' 00:00:00'

        df["reviewTime"] = cudf.to_datetime(reviewTime, format="%m-%d-%Y %H:%M:%S")
        df["isWeekend"] = (df["reviewTime"].dt.dayofweek >= 5).astype('int8')

        # === QUESTION DETECTION ===
        df["containsQuestion"] = df["reviewText"].str.contains(r"\?").astype('int8')

        # === MEMORY CLEANUP ===
        gc.collect()
        cuda.current_context().deallocations.clear()
        return df[['reviewText', 'productRating', 'reviewLength', 'isWeekend', 'containsQuestion']]
    except Exception as e:
        error_message = e.args[0]
        function_name = inspect.currentframe().f_code.co_name
        exception_class = get_full_class_name(e)
        file_name = os.path.basename(__file__)

        e.args = (error_message, function_name, file_name, exception_class)
        raise e
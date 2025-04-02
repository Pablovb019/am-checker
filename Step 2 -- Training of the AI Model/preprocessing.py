import cudf
import gc
from numba import cuda


def execute(df):
    # === COLUMN OPERATIONS ===
    df.insert(0, 'id', df['_id'].struct.field('$oid').astype("str"))
    df["id"] = df["id"].str.replace(r"[{}\"\']", "", regex=True)
    df.drop(columns=['category', '_id', 'reviewerID', 'reviewerName'], inplace=True)
    df = df.rename(columns={"overall": "productRating"})

    # === TEXT PREPROCESSING ===
    for col_name, length_col in [('reviewText', 'reviewLength'), ('summary', 'summaryLength')]:
        df[col_name] = df[col_name].str.lower().str.replace(r"[^a-z0-9'\s]", "", regex=True)
        df[length_col] = df[col_name].str.len()

    # === NUMERICAL PREPROCESSING ===
    df = df[df['reviewText'].str.len() > 15]
    df['reviewLength'] = df['reviewText'].str.len().astype('int16') # Update length after filtering

    # === TEMPORAL FEATURES ===
    df["reviewTime"] = cudf.to_datetime(df["unixReviewTime"], unit='s')
    df["isWeekend"] = (df["reviewTime"].dt.dayofweek >= 5).astype('int8')

    # === MEMORY CLEANUP ===
    gc.collect()
    cuda.current_context().deallocations.clear()

    # === CATEGORICAL FEATURES ===
    df['containsQuestion'] = df['reviewText'].str.contains(r"\?").astype('int8')

    # === SAMPLING ===
    df = df.groupby('asin').sample(frac=0.7, random_state=42)

    return df
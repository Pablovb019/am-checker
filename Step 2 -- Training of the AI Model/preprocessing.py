import cudf
import os
import pickle
from cuml.preprocessing import KBinsDiscretizer
import gc
from numba import cuda
import cupy as cp


def execute(df):
    # === COLUMN OPERATIONS ===
    df.insert(0, 'id', df['_id'].struct.field('$oid').astype("str"))
    df["id"] = df["id"].str.replace(r"[{}\"\']", "", regex=True)
    df.drop(columns=['category', '_id', 'reviewerID', 'reviewerName'], inplace=True)
    df = df.rename(columns={"overall": "productRating"})

    # === HELPFUL FEATURES ===
    helpful_0 = df["helpful"].list.get(0)
    helpful_1 = df["helpful"].list.get(1)
    df["reviewUpvotes"] = helpful_0
    df["helpfulTotalRatio"] = cp.where(helpful_1 == 0, 0.0, (helpful_0 / (helpful_1 + 1e-8)) * 100)  # Add epsilon

    # === TEXT PREPROCESSING ===
    for col_name, length_col in [('reviewText', 'reviewLength'), ('summary', 'summaryLength')]:
        df[col_name] = df[col_name].str.lower().str.replace(r"[^a-z0-9'\s]", "", regex=True)
        df[length_col] = df[col_name].str.len()

    # Remove empty/short reviews
    df = df[df['reviewText'].str.len() > 15]
    df['reviewLength'] = df['reviewText'].str.len().astype('int16') # Update length after filtering

    # === TEMPORAL FEATURES ===
    df["reviewTime"] = cudf.to_datetime(df["unixReviewTime"], unit='s')
    df["isWeekend"] = (df["reviewTime"].dt.dayofweek >= 5).astype('int8')

    # === PRODUCT STATS ===
    df["productPopularity"] = df.groupby("asin")["id"].transform("count").astype('int16')
    df["avgProductRating"] = df.groupby("asin")["productRating"].transform("mean")

    # === DISCRETIZATION ===
    discretizer_path = "ML_Models/discretizer.pkl"

    if os.path.exists(discretizer_path):
        print("Discretizador encontrado. Cargando...")
        with open(discretizer_path, "rb") as f:
            discretizer = pickle.load(f)
        df['helpfulRatioCategory'] = discretizer.transform(df[['helpfulTotalRatio']])
    else:
        print("Discretizador no encontrado. Creando...")
        discretizer = KBinsDiscretizer(
            n_bins=3,
            encode='ordinal',
            strategy='quantile'
        )
        discretizer.fit(df[['helpfulTotalRatio']])
        with open(discretizer_path, "wb") as f:
            pickle.dump(discretizer, f)

        df['helpfulRatioCategory'] = discretizer.transform(df[['helpfulTotalRatio']])

    del discretizer
    gc.collect()
    cuda.current_context().deallocations.clear()

    df["helpfulRatioCategory"] = df["helpfulRatioCategory"].map({0: "Low", 1: "Medium", 2: "High"})
    df['containsQuestion'] = df['reviewText'].str.contains(r"\?").astype('int8')

    # === SAMPLING ===
    df = df.groupby('asin').sample(frac=0.1, random_state=42)
    return df
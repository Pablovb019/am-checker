import cudf
from cuml.feature_extraction._tfidf_vectorizer import TfidfVectorizer
from cuml.preprocessing import KBinsDiscretizer
import cupy as cp
from nltk.corpus import stopwords
from cuml import UMAP


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
    if df['helpfulTotalRatio'].var() > 1e-4:
        discretizer = KBinsDiscretizer(
            n_bins=3,
            encode='ordinal',
            strategy='quantile'  # Only supported parameters
        )
        df['helpfulRatioCategory'] = discretizer.fit_transform(df[['helpfulTotalRatio']])
        df["helpfulRatioCategory"] = df["helpfulRatioCategory"].map({0: "Low", 1: "Medium", 2: "High"})
    else:
        df['helpfulRatioCategory'] = "Medium"  # Default value

    df['containsQuestion'] = df['reviewText'].str.contains(r"\?").astype('int8')

    # === SAMPLING ===
    df = df.groupby('asin').sample(frac=0.001, random_state=42)
    return df
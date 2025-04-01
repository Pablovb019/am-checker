import os
import pickle
import cudf
import time
import gc
from numba import cuda
from cuml.feature_extraction.text import TfidfVectorizer
from cuml.preprocessing import train_test_split
from cuml.metrics import accuracy_score, roc_auc_score
from imblearn.under_sampling import RandomUnderSampler
from sklearn.metrics import f1_score, matthews_corrcoef
from xgboost import XGBClassifier

def train(df, model_path="ML_Models/model.pkl", vectorizer_path="ML_Models/vectorizer.pkl"):
    training_time = time.time()
    # === DUPLICATE CHECK ===
    df = df[~df.index.duplicated()]  # Remove duplicates if any

    # === CHECK IF MODEL EXISTS AND LOAD ===
    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        # Model exists, load from disk
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        with open(vectorizer_path, "rb") as f:
            vectorizer = pickle.load(f)
        print("Modelo y vectorizer cargados desde disco.")

        model._booster = model.get_booster()  # Load XGBoost model

        # === TF-IDF FEATURES ===
        tfidf_features = vectorizer.transform(df['reviewText']).toarray()
        print("TF-IDF Actualizado con los datos de este dataset.")

    else:
        # Model does not exist, train from scratch
        print("Modelo y vectorizer no encontrados. Entrenando desde cero.")
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1000)
        model = XGBClassifier(
            device='cuda', tree_method='gpu_hist', predictor='gpu_predictor', objective='multi:softmax',
            enable_categorical=True, num_class=len(df['class'].unique()), n_estimators=500,
            learning_rate=0.1, max_depth=6, use_label_encoder=False, eval_metric='mlogloss',
            subsample=0.8, reg_alpha=0.5, reg_lambda=0.5, verbosity=0
        )

        # === TF-IDF FEATURES ===
        tfidf_features = vectorizer.fit_transform(df['reviewText']).toarray()
        print("TF-IDF Entrenado con los datos de este dataset.")

    # === cuDF DATAFRAME ===
    df = df.reset_index(drop=True)
    tfidf_df = cudf.DataFrame(tfidf_features).reset_index(drop=True)
    tfidf_df.columns = [f'tfidf_{i}' for i in range(tfidf_features.shape[1])]

    # === MERGE TF-IDF FEATURES ===
    feature_cols = ['helpfulTotalRatio', 'reviewLength', 'isWeekend', 'productPopularity', 'avgProductRating', 'containsQuestion']
    tabular_features = df[feature_cols].reset_index(drop=True).rename(columns=lambda x: f'tab_{x}')

    features = cudf.concat([tfidf_df, tabular_features], axis=1)
    df_class = df['class']

    # == MEMORY CLEANUP 1 ==
    del tfidf_features, tfidf_df, tabular_features, df
    gc.collect()
    cuda.current_context().deallocations.clear()

    # === DATA SPLITTING ===
    print("Dividiendo datos en entrenamiento y prueba...")
    X_train, X_test, y_train, y_test = train_test_split(
        features, df_class, test_size=0.3, random_state=42, stratify=df_class
    )
    print("Datos divididos.")

    # === REBALANCE DATASET ===
    X_train_pd = X_train.to_pandas()
    y_train_pd = y_train.to_pandas()

    rus = RandomUnderSampler(random_state=42)
    X_train_res, y_train_res = rus.fit_resample(X_train_pd, y_train_pd)

    X_train_res = cudf.DataFrame.from_pandas(X_train_res)
    y_train_res = cudf.Series(y_train_res)

    # == MEMORY CLEANUP 2 ==
    del features, X_train, X_train_pd, y_train_pd, df_class, rus
    gc.collect()
    cuda.current_context().deallocations.clear()

    # === TRAINING ===
    print("Entrenando modelo...\n")
    if os.path.exists(model_path):
        xgbModel = model
    else:
        xgbModel = None

    model.fit(
        X_train_res,
        y_train_res,
        xgb_model=xgbModel,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    preds = model.predict(X_test)
    preds = cudf.Series(preds)

    # === METRICS ===
    acc = accuracy_score(y_test, preds.astype('int64'))
    f1 = f1_score(y_test.to_pandas(), preds.to_pandas(), average='weighted')
    auc = roc_auc_score(y_test, preds)
    mcc = matthews_corrcoef(y_test.to_pandas(), preds.to_pandas())

    print("### METRICS ###")
    print(f"Accuracy: {acc:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"AUC: {auc:.4f}")
    print(f"MCC: {mcc:.4f}")

    # === SAVE MODEL AND VECTORIZER ===
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"Tiempo de entrenamiento: {time.time() - training_time:.2f} segundos")
    print("Modelo y vectorizer guardados en disco.")
import cudf
import time
from cuml import LogisticRegression, RandomForestClassifier
from cuml.feature_extraction.text import TfidfVectorizer
from cuml.preprocessing import train_test_split
from imblearn.under_sampling import RandomUnderSampler
import matplotlib.pyplot as plt
import seaborn as sns
from cuml.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sklearn.metrics import f1_score, matthews_corrcoef
from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier
import gc
from numba import cuda
import cupy as cp


def execute_mL(df):
    # === DUPLICATE CHECK ===
    df = df[~df.index.duplicated()]  # Remove duplicates if any

    # === TF-IDF FEATURES ===
    print("Extrayendo características TF-IDF...")
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1000)
    tfidf_features = vectorizer.fit_transform(df['reviewText']).toarray()
    print("Características TF-IDF extraídas.")

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
    print("Entrenando modelos...\n")

    # === MODEL INITIALIZATION ===
    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000),
        "Random Forest": RandomForestClassifier(n_estimators=100),
        "Decision Tree": DecisionTreeClassifier(max_depth=12, min_samples_leaf=20),
        "Gradient Boosting": XGBClassifier(
            device='cuda', tree_method='gpu_hist', predictor='gpu_predictor', objective='multi:softmax',
            num_class=len(y_train.unique()), n_estimators=500, learning_rate=0.1,
            max_depth=6, use_label_encoder=False, eval_metric='mlogloss',
            subsample=0.8, reg_alpha=0.5, reg_lambda=0.5, verbosity=0
        )
    }

    results = {}

    # === MODEL TRAINING ===
    for name, model in models.items():
        model_time = time.time()
        # Train model
        if "Gradient" in name or "Decision" in name:
            if name == "Gradient Boosting":
                model.fit(
                    X_train_res,
                    y_train_res,
                    eval_set=[(X_test, y_test)],
                    verbose=False
                )
                preds = model.predict(X_test)
            else:
                X_train_pd = X_train_res.to_pandas()
                y_train_pd = y_train_res.to_pandas()
                model.fit(X_train_pd, y_train_pd)
                preds = model.predict(X_test.to_pandas())

            preds = cudf.Series(preds) # Common to both Gradient Boosting models and Decision Tree

        else:
            model.fit(X_train_res, y_train_res)
            preds = model.predict(X_test)

        # Calculate metrics
        acc = accuracy_score(y_test, preds.astype('int64'))
        f1 = f1_score(y_test.to_pandas(), preds.to_pandas(), average='weighted')
        auc = roc_auc_score(y_test, preds)
        mcc = matthews_corrcoef(y_test.to_pandas(), preds.to_pandas())


        results[name] = {'Accuracy': acc, 'F1': f1, 'AUC': auc, 'MCC': mcc, 'Time': time.time() - model_time}

        print(f"### {name.upper()} ###")
        print(f"Accuracy: {results[name]['Accuracy']:.4f}")
        print(f"F1 Score: {results[name]['F1']:.4f}")
        print(f"AUC: {results[name]['AUC']:.4f}")
        print(f"MCC: {results[name]['MCC']:.4f}")
        print(f"Tiempo de entrenamiento: {results[name]['Time']:.2f} segundos")
        print("\n\n")
        plot_confusion_matrix(y_test, preds, name)

        # Free memory
        del model, preds
        gc.collect()
        cuda.current_context().deallocations.clear()

    # === PLOT MODEL COMPARISON ===
    plot_model_comparison(results)


def plot_confusion_matrix(y_true, y_pred, title):
    cm = confusion_matrix(y_true.astype('int64'), y_pred.astype('int64'))
    if hasattr(cm, "get"):
        cm = cm.get()

    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt="d")
    plt.title(f"Confusion Matrix - {title}")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()


def plot_model_comparison(results):
    models = list(results.keys())
    accuracies = [results[m]["Accuracy"] for m in models]

    plt.figure(figsize=(12, 6))
    plt.bar(models, accuracies, color=['#4CAF50', '#2196F3', '#FF9800', '#F44336'])
    plt.title("Comparación de Modelos (Accuracy)")
    plt.ylabel("Accuracy")
    plt.ylim(0.7, 1.0)

    for i, v in enumerate(accuracies):
        plt.text(i, v + 0.02, f"{v:.4f}", ha='center')

    plt.show()
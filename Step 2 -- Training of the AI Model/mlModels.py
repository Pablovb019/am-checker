import cudf
from cuml import LogisticRegression, RandomForestClassifier
from cuml.feature_extraction.text import TfidfVectorizer
from cuml.preprocessing import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from cuml.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sklearn.metrics import f1_score
import lightgbm as lgb


def execute_mL(df):
    # === DUPLICATE CHECK ===
    df = df[~df.index.duplicated()]  # Remove duplicates if any

    # === TF-IDF FEATURES ===
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)
    tfidf_features = vectorizer.fit_transform(df['reviewText']).toarray()

    # === cuDF DATAFRAME ===
    df = df.reset_index(drop=True)
    tfidf_df = cudf.DataFrame(tfidf_features).reset_index(drop=True)
    tfidf_df.columns = [f'tfidf_{i}' for i in range(tfidf_features.shape[1])]


    # === MERGE TF-IDF FEATURES ===
    feature_cols = ['helpfulTotalRatio', 'reviewLength', 'isWeekend', 'productPopularity', 'avgProductRating', 'containsQuestion']
    tabular_features = df[feature_cols].reset_index(drop=True).rename(columns=lambda x: f'tab_{x}')
    features = cudf.concat([tfidf_df, tabular_features], axis=1)

    # === DATA SPLITTING ===
    X_train, X_test, y_train, y_test = train_test_split(
        features, df['class'], test_size=0.3, random_state=42, stratify=df['class']
    )

    # === MODEL INITIALIZATION ===
    models = {
        "Logistic Regression": LogisticRegression(max_iter=2000),
        "Random Forest": RandomForestClassifier(n_estimators=100),
        "Gradient Boosting": lgb.LGBMClassifier(
            device='cuda', objective='multiclass', num_class=len(y_train.unique()),
            n_estimators=500, learning_rate=0.05, max_depth=8,
            num_leaves=127, verbose=-1
        ),
        "Decision Tree": lgb.LGBMClassifier(
            device='cuda', objective='multiclass', num_class=len(y_train.unique()),
            n_estimators=1, max_depth=12, learning_rate=0.8,
            min_child_samples=20, verbose=-1
        )
    }

    results = {}

    # === MODEL TRAINING ===
    for name, model in models.items():
        # Train model
        if "Gradient" in name or "Decision" in name:
            X_train_pd = X_train.to_pandas()
            y_train_pd = y_train.to_pandas()
            X_test_pd = X_test.to_pandas()
            y_test_pd = y_test.to_pandas()

            model.fit(
                X_train_pd,
                y_train_pd,
                eval_set=[(X_test_pd, y_test_pd)],
                eval_metric='multi_logloss'
            )

            preds = model.predict(X_test.to_pandas())
            preds = cudf.Series(preds)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

        # Calculate metrics
        acc = accuracy_score(y_test, preds.astype('int64'))
        f1 = f1_score(y_test.to_pandas(), preds.to_pandas(), average='weighted')
        auc = roc_auc_score(y_test, preds)


        results[name] = {'Accuracy': acc, 'F1': f1, 'AUC': auc}

        print(f"{name} - Accuracy: {acc:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}")
        plot_confusion_matrix(y_test, preds, name)

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
    plt.bar(models, accuracies, color=['#4CAF50', '#2196F3', '#FF9800'])
    plt.title("Comparación de Modelos (Accuracy)")
    plt.ylabel("Accuracy")
    plt.ylim(0.7, 1.0)

    for i, v in enumerate(accuracies):
        plt.text(i, v + 0.02, f"{v:.4f}", ha='center')

    plt.show()
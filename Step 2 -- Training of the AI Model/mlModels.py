import numpy as np
from cuml import LogisticRegression, RandomForestClassifier
from cuml.preprocessing import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from cuml.metrics import accuracy_score, confusion_matrix, roc_auc_score
import lightgbm as lgb
import cupy as cp


def calculate_f1(cm):
    """Manual F1 calculation that works for both binary and multiclass"""
    if len(cm.shape) == 2 and cm.shape[0] == 2:  # Binary case
        tn, fp, fn, tp = cm.ravel()
        precision = tp / (tp + fp) if (tp + fp) != 0 else 0
        recall = tp / (tp + fn) if (tp + fn) != 0 else 0
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0
    else:  # Multiclass - calculate weighted F1
        tp = np.diag(cm)
        fp = cm.sum(axis=0) - tp
        fn = cm.sum(axis=1) - tp

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)

        f1 = 2 * (precision * recall) / (precision + recall)
        f1[np.isnan(f1)] = 0  # Handle division by zero

        # Weighted average
        support = cm.sum(axis=1)
        return np.sum(f1 * support) / support.sum()


def execute_mL(df):
    df['class'] = df['class'].astype('int32')

    # === CONVERT STRING FEATURES TO GPU ARRAYS ===
    features_array = cp.array([
        [float(x) for x in vec.split() if x]
        for vec in df['features'].fillna('').to_arrow().to_pylist()
    ])

    # === TABULAR FEATURES ===
    feature_cols = ['helpfulTotalRatio', 'reviewLength', 'isWeekend', 'productPopularity', 'avgProductRating', 'containsQuestion']
    tabular_features = df[feature_cols].values

    # === COMBINE ALL FEATURES ===
    X = cp.hstack([features_array, tabular_features])
    y = df['class'].values

    # === DATA SPLITTING ===
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.3,
        random_state=42,
        stratify=y
    )

    # === DYNAMIC CLASS HANDLING ===
    num_classes = len(cp.unique(y_train))
    print(f"Number of Classes: {num_classes}")

    # === MODEL PARAMETERS ===
    params_gdb = {
        "device": "cuda",
        "boosting_type": "gbdt",
        "objective": "multiclass",
        "num_class": num_classes,
        "max_depth": 5,
        "n_estimators": 100,
        "learning_rate": 0.1,
        "num_leaves": 31,
        "min_child_samples": 20,
        "reg_alpha": 0.1,
        "reg_lambda": 0.1,
        "force_col_wise": True,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "early_stopping_rounds": 20,
        "metric": "multi_logloss",
        "verbose": -1
    }

    params_dt = {
        "device": "cuda",
        "boosting_type": "gbdt",
        "objective": "multiclass",
        "num_class": num_classes,
        "n_estimators": 1,
        "max_depth": -1,
        "num_leaves": 255,
        "min_child_samples": 1,
        "learning_rate": 1.0,
        "feature_fraction": 1.0,
        "bagging_freq": 0,
        "reg_alpha": 0.0,
        "reg_lambda": 0.0,
        "force_col_wise": True,
        "early_stopping_rounds": 20,
        "verbose": -1
    }

    # === MODEL DEFINITION ===
    models = {
        "Decision Tree": lgb.LGBMClassifier(**params_dt),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=20),
        "Logistic Regression": LogisticRegression(max_iter=2000, penalty='l2', C=1.0),
        "Gradient Boosting": lgb.LGBMClassifier(**params_gdb)
    }

    # === TRAINING LOOP ===
    results = {}
    for name, model in models.items():
        X_train_np = X_train.get() if isinstance(X_train, cp.ndarray) else X_train
        y_train_np = y_train.get() if isinstance(y_train, cp.ndarray) else y_train
        X_test_np = X_test.get() if isinstance(X_test, cp.ndarray) else X_test
        y_test_np = y_test.get() if isinstance(y_test, cp.ndarray) else y_test

        if "Gradient Boosting" in name or "Decision Tree" in name:
            # LightGBM requires validation set for early stopping
            model.fit(
                X_train_np,
                y_train_np,
                eval_set=[(X_test_np, y_test_np)],
                eval_metric='multi_logloss'
            )
        else:
            # Other models (cuML)
            model.fit(X_train_np, y_train_np)

        # === PREDICT PROBABILITIES FOR AUC ===
        auc = 0.0
        if hasattr(model, "predict_proba"):
            predictions_proba = model.predict_proba(X_test_np)
            auc = roc_auc_score(y_test, predictions_proba[:, 1])

        predictions = cp.asarray(model.predict(X_test_np), dtype='int32')

        # === METRICS ===
        cm = confusion_matrix(y_test.astype('int32') if isinstance(y_test, cp.ndarray) else cp.array(y_test.astype('int32')),predictions.astype('int32'))
        f1 = calculate_f1(cm.get() if hasattr(cm, "get") else cm)

        results[name] = {
            "Accuracy": accuracy_score(y_test, predictions),
            "F1-Score": f1,
            "AUC": auc,
        }

        print(f"\n=== {name} ===")
        print(f"Test Accuracy: {results[name]['Accuracy']:.4f}")
        print(f"F1-Score: {results[name]['F1-Score']:.4f}")
        print(f"AUC: {results[name]['AUC']:.4f}")

        plot_confusion_matrix(y_test, predictions, name)

    plot_model_comparison(results)


def plot_confusion_matrix(y_true, y_pred, title):
    cm = confusion_matrix(y_true, y_pred)
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
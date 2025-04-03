import inspect
import os

import cudf
import step2.preprocessing as pre
import step2.database as db
import pickle
import gc
from numba import cuda
from step1.utilities.logger import Logger

def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__

def predict(product_id, reviews):
    if not db.check_predictions(product_id):
        Logger.warning("Product has not been predicted yet. Proceeding with prediction.")
        model_path = 'step2/ML/model.pkl'
        vectorizer_path = 'step2/ML/vectorizer.pkl'

        Logger.info("Loading model and vectorizer...")
        # Load the model and vectorizer
        with open(model_path, 'rb') as f:
            model = pickle.load(f)

        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)

        Logger.success("Model and vectorizer loaded successfully.")

        try:
            Logger.info("Preprocessing reviews for model prediction...")
            # Preprocess the reviews, and return them in a cudf DataFrame
            df = pre.preprocess_reviews(product_id, reviews)
            Logger.success("Reviews preprocessed successfully.")

            # TF-IDF Features
            Logger.info("Vectorizing reviews for model prediction...")
            tfidf_features = vectorizer.transform(df['reviewText']).toarray()
            tfidf_df = cudf.DataFrame(tfidf_features)
            tfidf_df.columns = [f"tfidf_{i}" for i in range(tfidf_features.shape[1])]
            Logger.success("Reviews vectorized successfully.")

            # Tabular features
            Logger.info("Combining tabular features for model prediction")
            tabular_features = df[['reviewLength', 'isWeekend', 'containsQuestion']]
            tabular_features.columns = [f'tab_{col}' for col in tabular_features.columns]

            # Combine features
            features = cudf.concat([tfidf_df, tabular_features], axis=1)
            Logger.success("Features combined successfully.")

            # Predict
            Logger.info("Making predictions...")
            predictions = model.predict_proba(features)[:, 1] # Probability of class 1 (being SPAM review)
            Logger.success("Predictions made successfully.")

            # Memory cleanup
            del df, tfidf_df, tabular_features, features, model, vectorizer, tfidf_features
            gc.collect()
            cuda.current_context().deallocations.clear()

            # Add predictions to reviews list
            Logger.info("Adding predictions to reviews...")
            predictions = predictions.tolist()

            for i, review in enumerate(reviews):
                review['ml_predict'] = round(float(predictions[i]), 4)
            Logger.success("Predictions added successfully.")

            avg_pred = round(sum(predictions) / len(predictions), 4)

            Logger.info("Saving predictions to database...")
            db.update_reviews(product_id, reviews)
            db.update_product(product_id, avg_pred)
            Logger.success("Predictions saved successfully.")
            return reviews

        except Exception as e:
            if len(e.args) == 4:
                raise e
            else:
                error_message = e.args[0]
                function_name = inspect.currentframe().f_code.co_name
                exception_class = get_full_class_name(e)
                file_name = os.path.basename(__file__)

                e.args = (error_message, function_name, file_name, exception_class)
                raise e
        finally:
            gc.collect()
            cuda.current_context().deallocations.clear()
    else:
        Logger.success("Product has already been predicted. Loading predictions from database.")
        try:
            reviews = db.load_reviews(product_id)
            Logger.success("Predictions loaded successfully.")
            return reviews
        except Exception as e:
            if len(e.args) == 4:
                raise e
            else:
                error_message = e.args[0]
                function_name = inspect.currentframe().f_code.co_name
                exception_class = get_full_class_name(e)
                file_name = os.path.basename(__file__)

                e.args = (error_message, function_name, file_name, exception_class)
                raise e
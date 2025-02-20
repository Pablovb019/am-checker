from utilities import scrapper as scr
from utilities import database as db

import pycountry
import datetime
import inspect
import os

from utilities.logger import Logger

def get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__

def amazon_exec(url, country_suffix):
    flag_noReviews = False
    flag_lastScan = False
    flag_noNewReviews = False

    country = 'GB' if country_suffix == 'co.uk' else 'US'
    country_name = pycountry.countries.get(alpha_2=country).name
    product_id = url.split("/dp/")[1].split("/")[0]

    Logger.info("Getting product info")
    product_info = scr.get_product_info(url, country_name, country_suffix)
    Logger.success("Product info obtained")
    Logger.info("Checking if product is in database")

    try:
        check_product = db.check_product(product_id)
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

    if check_product:
        Logger.success("Product is in database")
        last_scan = db.get_last_product_scan(product_id)

        if (datetime.datetime.now() - last_scan).days > 30:
            Logger.info("Last scan was more than a month ago. Rescanning for new reviews")
            flag_lastScan = True
            try:
                db.update_last_product_scan(product_id)
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

            Logger.info("Getting reviews")
            reviews = scr.get_reviews(country_name, country_suffix)
            Logger.success(f"Reviews obtained. Total reviews: {len(reviews)}")
        else:
            Logger.info("Last scan was less than a month ago. Not need for rescanning for new reviews")
            Logger.info(f"Loading reviews of product_id '{product_id}' from database")
            try:
                reviews = db.load_reviews(product_id)
                Logger.success(f"Loaded reviews of product_id '{product_id}' from database. Total reviews: {len(reviews)}")
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
    else:
        Logger.warning("Product is not in database. Saving product info")
        try:
            db.save_product(product_id, product_info)
            Logger.success("Product info saved in database")
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

    if not check_product or flag_lastScan:
        Logger.info("Getting reviews")
        reviews = scr.get_reviews(country_name, country_suffix, product_info["rating"])
        print("\n") # for output purposes
        Logger.success(f"Reviews obtained. Total reviews: {len(reviews)}")

        if not reviews:
            Logger.info("No reviews obtained")
            flag_noReviews = True
            Logger.info("Deleting product from database")
            try:
                db.delete_product(product_id)
                Logger.success("Product deleted from database")
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

        if not flag_noReviews:
            Logger.info("Checking for repeated reviews")
            reviews = scr.remove_repeated_reviews(reviews)
            Logger.success(f"Repeated reviews removed. Total reviews: {len(reviews)}")

            if flag_lastScan:
                Logger.info("Checking if new reviews where obtained")
                reviews = [review for review in reviews if not db.check_review(review["id"])]
                if not reviews:
                    Logger.success("No new reviews where obtained")
                    flag_noNewReviews = True

            if not flag_noNewReviews:
                Logger.info("Saving reviews in database")
                try:
                    reviews = scr.normalize_reviews(reviews, country_suffix)
                    db.save_reviews(product_id, reviews)
                    Logger.success("Reviews saved in database")
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
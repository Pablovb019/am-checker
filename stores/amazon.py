from utilities import scrapper as scr

import pycountry
import logging


def amazon_exec(url, country_suffix):
    country = 'GB' if country_suffix == 'co.uk' else 'US'
    country_name = pycountry.countries.get(alpha_2=country).name

    logging.info("Getting product info")
    product_info = scr.get_product_info(url, country_name, country_suffix)
    logging.info("Product info obtained")

    logging.info("Getting reviews")
    reviews = scr.get_reviews(country_name, country_suffix)
    logging.info(f"Reviews obtained. Total reviews: {len(reviews)}")

    logging.info("Checking for repeated reviews")
    reviews = scr.remove_repeated_reviews(reviews)
    logging.info(f"Repeated reviews removed. Total reviews: {len(reviews)}")

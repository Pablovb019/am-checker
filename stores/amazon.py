import scrapper as scr

import tldextract
import pycountry
import logging

def amazon_exec(url, country_suffix):
    country = 'GB' if country_suffix == 'co.uk' else 'US'
    country_name = pycountry.countries.get(alpha_2=country).name

    logging.info(f"Doing Login in Amazon {country_name}")

    scr.login(country_suffix)
    logging.info("Login done")
    logging.info("Getting product info")

    product_info = scr.get_product_info(url)
    logging.info("Product info obtained")

    logging.info("Getting reviews")
    reviews = scr.get_reviews(country_name)
    logging.info(f"Reviews obtained. Total reviews: {len(reviews)}")
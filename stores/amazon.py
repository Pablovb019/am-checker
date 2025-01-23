import scrapper as scr

import tldextract
import pycountry
import logging
import requests

from bs4 import BeautifulSoup
from faker import Faker

def amazon_exec(url):
    amazon_country = tldextract.extract(url).suffix
    country_name = pycountry.countries.get(alpha_2=amazon_country).name

    logging.info(f"Doing Login in Amazon {country_name}")

    scr.login(amazon_country)
    logging.info("Login done")
    logging.info("Getting product info")

    product_info = scr.get_product_info(url)
    logging.info("Product info obtained")

    logging.info("Getting reviews")
    reviews = scr.get_reviews()
    logging.info("Reviews obtained")
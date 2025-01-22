import scrapper as scr

import tldextract
import pycountry
import logging
import requests

from bs4 import BeautifulSoup
from faker import Faker

def amazon_exec(url):
    amazon_country = tldextract.extract(url).suffix
    scr.login(amazon_country)
    print("Login correcto")
    # product_info = scr.get_product_info(product_id)

    # print("Nombre del producto:", product_info["product_name"])
    # print("Precio del producto:", product_info["product_price"])
    # print("Valoracion del producto:", product_info["product_rating"])
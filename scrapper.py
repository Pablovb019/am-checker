from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import globals


def login(country):
    # Create a new instance of Chrome
    driver = globals.driver

    driver.get(f"https://www.amazon.{country}/gp/sign-in.html")

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(os.getenv('AMAZONTEST_EMAIL'))
    driver.find_element(By.ID, "continue").click()

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(os.getenv('AMAZONTEST_PASSWORD'))
    driver.find_element(By.ID, "signInSubmit").click()

def get_product_info(product_id):
    driver = globals.driver
    driver.get(f"https://www.amazon.com/dp/{product_id}")

    #Obtain product name, price, and rating
    product_name = driver.find_element(By.ID, "productTitle").text
    product_price = driver.find_element(By.ID, "priceblock_ourprice").text
    product_rating = driver.find_element(By.ID, "acrPopover").get_attribute("title")

    product_info = {
        "product_name": product_name,
        "product_price": product_price,
        "product_rating": product_rating
    }

    return product_info
import logging

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
    WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

def get_product_info(url):
    driver = globals.driver
    driver.get(url)

    name = driver.find_element(By.ID, "productTitle").text
    price = driver.find_element(By.CLASS_NAME, "a-price").text.replace("\n", ",")
    rating = driver.find_element(By.ID, "acrPopover").get_attribute("title").split(" ")[0] + "/5"

    product_info = {
        "product_name": name,
        "product_price": price,
        "product_rating": rating
    }

    return product_info

def get_reviews():
    driver = globals.driver
    driver.get(driver.find_element(By.CSS_SELECTOR, '[data-hook="see-all-reviews-link-foot"]').get_attribute("href"))

    total_reviews = 100 # Amazon Limit for reviews, only 100 reviews are shown
    logging.info(f"Total reviews: {total_reviews}")

    reviews = []
    while len(reviews) < total_reviews:
        reviews_page = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review"]')
        for review in reviews_page:
            logging.info(f"Review Progress [{len(reviews)+1}/{total_reviews}] {round(len(reviews)+1 / total_reviews * 100, 2)}%")
            review_author = review.find_element(By.CSS_SELECTOR, '.a-profile-name').text
            review_rating = driver.execute_script("return arguments[0].textContent;", review.find_element(By.CSS_SELECTOR, '[data-hook="review-star-rating"] .a-icon-alt')).split(" ")[0] + "/5"
            review_date = review.find_element(By.CSS_SELECTOR, '[data-hook="review-date"]').text
            review_title = review.find_element(By.CSS_SELECTOR, '[data-hook="review-title"]').text
            review_text = review.find_element(By.CSS_SELECTOR, '[data-hook="review-body"]').text
            review_verified = "Yes" if review.find_element(By.CSS_SELECTOR, '[data-hook="avp-badge"]').text else "No"

            reviews.append({
                "author": review_author,
                "rating": review_rating,
                "date": review_date,
                "title": review_title,
                "text": review_text,
                "verified": review_verified
            })
        # next page
        try:
            driver.get(f"{driver.current_url}&pageNumber={len(reviews)//10+1}")
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        except:
            break
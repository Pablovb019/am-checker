import logging
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

import os
import globals


def login(country):
    driver = globals.driver
    driver.get(f"https://www.amazon.{country}/gp/sign-in.html")

    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.NAME, "email"))).send_keys(os.getenv('AMAZONTEST_EMAIL'))
    driver.find_element(By.ID, "continue").click()

    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.NAME, "password"))).send_keys(os.getenv('AMAZONTEST_PASSWORD'))
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

def get_reviews(country_name):
    driver = globals.driver
    driver.get(driver.find_element(By.CSS_SELECTOR, '[data-hook="see-all-reviews-link-foot"]').get_attribute("href") + "&sortBy=helpful&reviewerType=all_reviews&filterByStar=all_star&pageNumber=1")
    reviews = []

    # Obtain all reviews (Sort By: Top reviews + Filter By: All reviews)
    reviews += get_reviews_recursive(country_name, driver, "Top Reviews", "All Reviews")
    url = reset_url(driver.current_url)

    # Obtain all reviews (Sort By: Top Reviews + Filter By: Verified Purchase Only)
    filter_by_verified_top_reviews = url.split("reviewerType=")[1].split("&")[0]
    url = url.replace(f"reviewerType={filter_by_verified_top_reviews}", "reviewerType=avp_only_reviews")
    driver.get(url)
    reviews += get_reviews_recursive(country_name, driver, "Top Reviews", "Verified Purchase Only")
    url = reset_url(driver.current_url)

    # Obtain all reviews (Sort By: Most Recent + Filter By: All reviews)
    filter_by_all_reviews_most_recent = url.split("sortBy=")[1].split("&")[0]
    url = url.replace(f"sortBy={filter_by_all_reviews_most_recent}", "sortBy=recent")
    driver.get(url)
    reviews += get_reviews_recursive(country_name, driver, "Most Recent", "All Reviews")
    url = reset_url(driver.current_url)

    # Obtain all reviews (Sort By: Most Recent + Filter By: Verified Purchase Only)
    filter_by_verified_most_recent = url.split("reviewerType=")[1].split("&")[0]
    url = url.replace(f"reviewerType={filter_by_verified_most_recent}", "reviewerType=avp_only_reviews")
    driver.get(url)
    reviews += get_reviews_recursive(country_name, driver, "Most Recent", "Verified Purchase Only")

    return reviews


def reset_url(url):
    page_number = url.split("pageNumber=")[1].split("&")[0]
    url = url.replace(f"pageNumber={page_number}", "pageNumber=1")

    filter_by_star = url.split("filterByStar=")[1].split("&")[0]
    url = url.replace(f"filterByStar={filter_by_star}", "filterByStar=all_star")
    return url

def get_reviews_recursive(country_name, driver, sort, type_filter):
    reviews = []

    # All stars reviews
    reviews += get_reviews_stars_recursive(country_name, driver, "All Stars", sort, type_filter)

    # Add all 5-star reviews
    url = reset_url(driver.current_url)
    url = url.replace("filterByStar=all_star", "filterByStar=five_star")
    driver.get(url)
    reviews += get_reviews_stars_recursive(country_name, driver, "5 Stars", sort, type_filter)

    # Add all 4-star reviews
    url = reset_url(driver.current_url)
    url = url.replace("filterByStar=all_star", "filterByStar=four_star")
    driver.get(url)
    reviews += get_reviews_stars_recursive(country_name, driver, "4 Stars", sort, type_filter)

    # Add all 3-star reviews
    url = reset_url(driver.current_url)
    url = url.replace("filterByStar=all_star", "filterByStar=three_star")
    driver.get(url)
    reviews += get_reviews_stars_recursive(country_name, driver, "3 Stars", sort, type_filter)

    # Add all 2-star reviews
    url = reset_url(driver.current_url)
    url = url.replace("filterByStar=all_star", "filterByStar=two_star")
    driver.get(url)
    reviews += get_reviews_stars_recursive(country_name, driver, "2 Stars", sort, type_filter)

    # Add all 1-star reviews
    url = reset_url(driver.current_url)
    url = url.replace("filterByStar=all_star", "filterByStar=one_star")
    driver.get(url)
    reviews += get_reviews_stars_recursive(country_name, driver, "1 Star", sort, type_filter)

    return reviews

def get_reviews_stars_recursive(country_name, driver, stars, sort, type_filter):
    product_review = driver.find_element(By.CSS_SELECTOR, '[data-hook="cr-filter-info-review-rating-count"]').text
    total_reviews = int(re.findall(r'\d+', product_review)[1].replace(",", ""))

    total_reviews = min(100, total_reviews) # Limit to 100 reviews, Amazon only shows 10 reviews per page and we can only scrape 10 pages
    logging.info(f"\n\nTotal reviews (including possible foreign review): {total_reviews}\n\n")

    reviews = []
    while len(reviews) < total_reviews:
        reviews_page = driver.find_elements(By.CSS_SELECTOR, '[data-hook="review"]')
        for review in reviews_page:
            if review.find_element(By.CSS_SELECTOR, '[data-hook="review-date"]').text.find(country_name) == -1:
                logging.info("Skipping Foreign Review")
                total_reviews -= 1
                continue
            logging.info(f"Review Progress ({sort}|{type_filter}|{stars}) {len(reviews)}/{total_reviews} [{len(reviews)/total_reviews*100:.1f}%]")
            review_author = review.find_element(By.CSS_SELECTOR, '.a-profile-name').text
            review_rating = driver.execute_script("return arguments[0].textContent;",review.find_element(By.CSS_SELECTOR,'[data-hook="review-star-rating"] .a-icon-alt')).split(" ")[0] + "/5"
            review_date = review.find_element(By.CSS_SELECTOR, '[data-hook="review-date"]').text
            review_title = review.find_element(By.CSS_SELECTOR, '[data-hook="review-title"]').text
            review_text = review.find_element(By.CSS_SELECTOR, '[data-hook="review-body"]').text

            reviews.append({
                "author": review_author,
                "rating": review_rating,
                "date": review_date,
                "title": review_title,
                "text": review_text,
            })
        # next page
        try:
            next_url = driver.current_url
            page_number = int(next_url.split("pageNumber=")[1].split("&")[0])
            next_url = next_url.replace(f"pageNumber={page_number}", f"pageNumber={page_number + 1}")
            driver.get(next_url)
            WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        except Exception as e:
            print("Error: ", e)

    return reviews
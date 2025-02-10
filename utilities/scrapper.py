import itertools

import utilities.globals as gl
import utilities.cookies as ck
import utilities.login as l

import logging
import re
import pandas as pd
import concurrent.futures
import queue

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

def get_product_info(url, country_name, country_suffix):
    driver = gl.driver
    if not ck.check_cookies(country_suffix):
        l.make_login(country_name, country_suffix)
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

def get_reviews(country_name, country_suffix):
    reviews = queue.Queue()  # Use a thread-safe queue for storing reviews
    driver = gl.driver

    try:
        base_url = driver.find_element(By.CSS_SELECTOR, '[data-hook="see-all-reviews-link-foot"]').get_attribute("href") + "&language=en_US&sortBy=helpful&reviewerType=all_reviews&filterByStar=all_star&pageNumber=1"
        logging.info("Starting to scrape reviews\n\n")

        stars_options = [1, 2, 3, 4, 5]
        sort_options = ["Top Reviews", "Most Recent"]
        type_filter_options = ["All Reviews", "Verified Purchase Only"]
        combinations = list(itertools.product(stars_options, sort_options, type_filter_options))

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for stars, sort, type_filter in combinations:
                futures.append(executor.submit(get_reviews_star_combo, country_name, country_suffix, base_url, stars, sort, type_filter))

            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    for review in result:
                        reviews.put(review)
                except Exception as e:
                    logging.error(f"Error processing combination: {e}")

    finally:
        driver.quit()

    return list(reviews.queue)

def get_reviews_star_combo(country_name, country_suffix, base_url, stars, sort, type_filter):
    reviews = []
    review_driver = None

    try:
        review_driver = webdriver.Firefox(options=gl.options)
        review_driver.get(f"https://www.amazon.{country_suffix}")
        ck.load_cookies(review_driver, f"cookies/amazon_{country_suffix}.pkl")
        logging.info(f"Scraping {stars}-star reviews ({sort}|{type_filter})")
        reviews = get_reviews_stars_recursive(country_name, base_url, review_driver, stars, sort, type_filter)
    except Exception as e:
        logging.error(f"Error in get_reviews_star_combo: {e}")
    finally:
        logging.info(f"Scraping {stars}-star reviews ({sort}|{type_filter}) -- DONE")
        if review_driver:
            review_driver.quit()
    return reviews

def get_reviews_stars_recursive(country_name, base_url, driver, stars, sort, type_filter):
    driver.get(base_url)
    url = driver.current_url
    page_number = url.split("pageNumber=")[1].split("&")[0]
    url = url.replace(f"pageNumber={page_number}", "pageNumber=1")

    if stars is not None:
        url = url.replace("filterByStar=all_star", f"filterByStar={stars}_star")

    if sort == "Top Reviews":
        url = url.replace("sortBy=helpful", "sortBy=helpful")
    elif sort == "Most Recent":
        url = url.replace("sortBy=helpful", "sortBy=recent")

    if type_filter == "Verified Purchase Only":
        url = url.replace("reviewerType=all_reviews", "reviewerType=avp_only_reviews")
    elif type_filter == "All Reviews":
        url = url.replace("reviewerType=avp_only_reviews", "reviewerType=all_reviews")

    driver.get(url)

    product_review = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, '[data-hook="cr-filter-info-review-rating-count"]'))).text
    total_reviews = int(re.findall(r'\d+', product_review)[1].replace(",", ""))
    foreign = False

    total_reviews = min(100, total_reviews) # Limit to 100 reviews, Amazon only shows 10 reviews per page and we can only scrape 10 pages
    reviews = []
    while len(reviews) < total_reviews:
        reviews_page = WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-hook="review"]')))
        for review in reviews_page:
            if review.find_element(By.CSS_SELECTOR, '[data-hook="review-date"]').text.find(country_name) == -1:
                foreign = True
                break

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

        if foreign:
            break # If a foreign review is found, stop scraping, continue with the next filter
        # next page
        try:
            next_url = driver.current_url
            page_number = int(next_url.split("pageNumber=")[1].split("&")[0])
            next_url = next_url.replace(f"pageNumber={page_number}", f"pageNumber={page_number + 1}")
            driver.get(next_url)
        except Exception as e:
            print("Error: ", e)

    return reviews

def remove_repeated_reviews(reviews):
    df = pd.DataFrame(reviews)
    df.drop_duplicates(subset=["text"])
    return df.to_dict(orient='records')
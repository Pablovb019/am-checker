import pickle
import os
import logging

def save_cookies(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)

def load_cookies(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

def check_cookies(country_suffix):
    if os.path.exists(f"cookies/amazon_{country_suffix}.pkl"):
        logging.info("Cookies found. Not need to login. Loading cookies")
        return True
    else:
        logging.info("Cookies not found. Redirecting to login process")
        return False
import step1.utilities.globals as gl
import step1.utilities.cookies as ck

import os

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from step1.utilities.logger import Logger

def make_login(country, suffix):
    Logger.info(f"Doing Login in Amazon {country}")
    driver = gl.driver
    driver.get(f"https://www.amazon.{suffix}/gp/sign-in.html")

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.NAME, "email")))
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.NAME, "email")))
    driver.find_element(By.NAME, "email").send_keys(os.getenv('AMAZONTEST_EMAIL'))
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.ID, "continue"))).click()

    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.NAME, "password")))
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.NAME, "password")))
    driver.find_element(By.NAME, "password").send_keys(os.getenv('AMAZONTEST_PASSWORD'))
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.ID, "signInSubmit"))).click()
    Logger.success("Login done. Saving cookies")

    ck.save_cookies(driver, f"step1/cookies/amazon_{suffix}.pkl")
from selenium import webdriver

def create_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    return webdriver.Firefox(options=options)

def close_driver(driver):
    driver.quit()

number_tasks = 20

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
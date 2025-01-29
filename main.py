import logging

import kagglehub
import tldextract

import stores.amazon as am
from globals import driver

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    url = input('URL of the product: ')
    url = url.split("/dp/")[0] + "/dp/" + url.split("/dp/")[1].split("/")[0] # Remove any extra characters from the URL

    if 'amazon' in url:
        print("Amazon URL detected")
        country_suffix = tldextract.extract(url).suffix
        if country_suffix != 'com' and country_suffix != 'co.uk':
            print("Sorry, only amazon.com and amazon.co.uk are supported. Try again.")
        else:
            am.amazon_exec(url, country_suffix)
            driver.quit() # Close the browser

        # Download latest version
        # path = kagglehub.dataset_download("naveedhn/amazon-product-review-spam-and-non-spam")
        # print("Path to dataset files:", path)
    else:
        print("Amazon URL not detected. Try again.")
import logging

import kagglehub
import tldextract

import stores.amazon as am
from globals import driver

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    url = input('Introduce la URL del producto: ')
    url = url.split("/dp/")[0] + "/dp/" + url.split("/dp/")[1].split("/")[0] # Remove any extra characters from the URL

    if 'amazon' in url:
        print("Amazon detectado")
        if tldextract.extract(url).suffix != 'com' or tldextract.extract(url).suffix != 'co.uk':
            print("Only amazon.com and amazon.co.uk are supported")
        else:
            am.amazon_exec(url)
            driver.quit() # Close the browser

        # Download latest version
        # path = kagglehub.dataset_download("naveedhn/amazon-product-review-spam-and-non-spam")
        # print("Path to dataset files:", path)
    else:
        print("No se ha detectado la tienda. Inténtalo de nuevo.")
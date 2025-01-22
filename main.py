import kagglehub
import tldextract

import stores.amazon as am
from globals import driver

if __name__ == '__main__':
    url = input('Introduce la URL del producto: ')

    if 'amazon' in url:
        print("Amazon detectado")
        if tldextract.extract(url).suffix == 'co.jp':
            print("Amazon Japan no está disponible de momento. Sentimos las molestias")
        else:
            am.amazon_exec(url)
            driver.quit() # Close the browser

        # Download latest version
        # path = kagglehub.dataset_download("naveedhn/amazon-product-review-spam-and-non-spam")
        # print("Path to dataset files:", path)
    else:
        print("No se ha detectado la tienda. Inténtalo de nuevo.")
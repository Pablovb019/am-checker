import stores.amazon as am

import tldextract
import requests

from utilities.logger import Logger

if __name__ == '__main__':
    url = input('URL of the product: ')
    if url.startswith("https://www.amazon."):
        if "/dp/" not in url:
            Logger.error("Invalid Amazon URL. It must be a product page (URL must contain '/dp/')")
        else:
            url = url.split("/dp/")[0] + "/dp/" + url.split("/dp/")[1].split("/")[0]  # Remove any extra characters from the URL
            if '?' in url:
                url = url.split("?")[0]
            Logger.info("Amazon URL detected")
            country_suffix = tldextract.extract(url).suffix
            if country_suffix != 'com' and country_suffix != 'co.uk':
                Logger.error("Sorry, only amazon.com and amazon.co.uk are supported. Try again.")
            else:
                response = requests.get(url)
                if response.status_code  != 200:
                    Logger.error(f"Invalid Amazon URL. Response {response.status_code}: {response.reason}")
                else:
                    try:
                        am.amazon_exec(url, country_suffix)
                    except Exception as e:
                        raised_function_name = e.args[1]
                        raised_exception_class = e.args[2]
                        Logger.error(f"Error obtaining amazon reviews\nFunction: {raised_function_name}\nException: {raised_exception_class}")

        # Download latest version
        # path = kagglehub.dataset_download("naveedhn/amazon-product-review-spam-and-non-spam")
        # print("Path to dataset files:", path)
    else:
        Logger.error("Amazon URL not detected. Try again.")
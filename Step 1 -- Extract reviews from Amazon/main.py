import stores.amazon as am
import utilities.globals as gl

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
                        gl.driver.quit()

                    except Exception as e:
                        raised_error_message = e.args[0]
                        raised_function_name = e.args[1]
                        raised_file = e.args[2]
                        raised_exception_class = e.args[3]

                        Logger.error(f"An error was captured obtaining Amazon reviews. Details below.\n- File: {raised_file}\n- Function: {raised_function_name} \n- Exception: {raised_exception_class}: {raised_error_message}")
    else:
        Logger.error("Amazon URL not detected. Try again.")
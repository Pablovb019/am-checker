import os
import requests
import logging

from bs4 import BeautifulSoup

def obtain_soup(url):
    api_key = os.getenv('SCRAPERAPI_KEY')
    if not api_key:
        print("No se ha encontrado la clave de ScraperAPI. Por favor, añádela a las variables de entorno.\n")
        return None

    try:
        payload = {'api_key' : api_key, 'url' : url}
        response = requests.get('http://api.scraperapi.com', params=payload)
        soup = BeautifulSoup(response.text, 'lxml')
        return soup

    except Exception as e:
        logging.error(f"Error al obtener la página con ScraperAPI: {e}\n")
        return None
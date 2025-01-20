import scrapper as scr

import tldextract
import pycountry
import logging

def amazon_exec(url):
    soup = scr.obtain_soup(url)
    if soup is not None:
        product, review = extract_data(soup)
        ext = tldextract.extract(url)

        # Extraemos el país de Amazon a partir de la URL
        country_code = 'US' if ext.suffix.split('.')[-1].upper() == 'COM' else ext.suffix.split('.')[-1].upper() # Si la URL es .com, el país es US, en caso contrario, se extrae el último fragmento de la URL (si es .es, el país es ES, o si es .co.uk, el país es UK)
        country_code = 'GB' if country_code == 'UK' else country_code # Amazon UK es GB, no UK
        amazon_country = pycountry.countries.get(alpha_2=country_code, default=None) # Obtenemos el país de Amazon a partir del código de país extraído usando la librería pycountry

        if '/s' in url or product is None: # Aseguramos que la URL sea un producto de Amazon, no una búsqueda o una categoría
            print("El enlace introducido no es válido. Por favor, introduzca un enlace válido a un producto de Amazon.\n")
        else:
            print(f"País de Amazon: Amazon {amazon_country.name if amazon_country else 'Desconocido'}")
            print(f"Nombre: {product.get('title')}")
            print(f"Valoración: {product.get('rating')}")
            print(f"Precio: {product.get('price')}")

            if not review:
                print("No se han encontrado reseñas del producto seleccionado\n\n")
            else:
                print(f"{len(review)} Reseñas encontradas\n\n")
                for rev in review:
                    print(f"Autor: {rev.get('author')}")
                    print(f"Valoración: {rev.get('rating')}")
                    print(f"Título: {rev.get('title')}")
                    print(f"Contenido: {rev.get('content')}")
                    print(f"Fecha: {rev.get('date')}")
                    print(f"Compra verificada: {rev.get('verified')}\n\n")

def extract_data(soup):
    try:
        title = soup.select_one('#productTitle').text.strip() if soup.select_one('#productTitle') else None
        rating = soup.select_one('#acrPopover').attrs['title'].split(' ')[0] + '/5' if soup.select_one('#acrPopover') else None
        price = soup.select_one('span.a-price span.a-offscreen').text.strip() if soup.select_one('span.a-price span.a-offscreen') else None
        object_data = {'title': title, 'rating': rating, 'price': price}

        reviews = []
        for review in soup.select('li.review') or []:
            rev_author = review.select_one('span.a-profile-name').text.strip() if review.select_one('span.a-profile-name') else None
            rev_rating = review.select_one('i.review-rating').text.strip() if review.select_one('i.review-rating') else None
            rev_title_element = review.select_one('a.review-title') or review.select_one('span.review-title')
            rev_title = (rev_title_element.select_one('span:not([class])') or rev_title_element.select_one('span.cr-original-review-content')).text.strip() if rev_title_element else None
            rev_content = review.select_one('span.review-text').text.strip().split('\n')[0] if review.select_one('span.review-text') else None
            rev_date = review.select_one('span.review-date').text.strip() if review.select_one('span.review-date') else None
            rev_verified = "Si" if review.select_one('span.a-size-mini') else "No"
            reviews.append({'author': rev_author, 'rating': rev_rating, 'title': rev_title, 'content': rev_content, 'date': rev_date, 'verified': rev_verified})

        return object_data, reviews


    except AttributeError as e:
        logging.error("Attribute error while extracting data: %s", e)
    except KeyError as e:
        logging.error("Key error while extracting data: %s", e)
    except Exception as e:
        logging.error("Unexpected error while extracting data: %s", e)

    return None, None
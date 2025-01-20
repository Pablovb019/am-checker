import kagglehub
import stores.amazon as am

if __name__ == '__main__':
    url = input('Introduce la URL del producto: ')

    if 'amazon' in url:
        print("Amazon detectado\n")
        am.amazon_exec(url)

        # Download latest version
        # path = kagglehub.dataset_download("naveedhn/amazon-product-review-spam-and-non-spam")
        # print("Path to dataset files:", path)
    else:
        print("No se ha detectado la tienda. Inténtalo de nuevo.")
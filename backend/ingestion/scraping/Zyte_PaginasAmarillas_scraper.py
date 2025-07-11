import requests
import os
from bs4 import BeautifulSoup
from backend.ingestion.scraping.normalizations import lower_text,normalize_URL_PaginasAmarillas,similarity
from base64 import b64decode

ZYTE_APIKEY=os.environ.get("ZYTE_APIKEY")

def search_for_business_paginas_amarillas(nombre_negocio, ciudad,province,direccion):
    # Formatear la URL de búsqueda en paginas_amarillas
    nombre_formateado = normalize_URL_PaginasAmarillas(nombre_negocio)
    ciudad_formateada = normalize_URL_PaginasAmarillas(ciudad)
    ciudad_minuscula= lower_text(ciudad)
    provincia_minuscula=lower_text(province)
    url = f"https://www.paginasamarillas.es/search/all-ac/all-ma/{provincia_minuscula}/all-is/{ciudad_minuscula}/all-ba/all-pu/all-nc/1?what={nombre_formateado}&where={ciudad_formateada}&ub=false&aprob=0.0&nprob=1.0&qc=true"
    #"https://www.paginasamarillas.es/search/all-ac/all-ma/cordoba/all-is/cordoba/all-ba/all-pu/all-nc/1?what=dobuss&where=C%C3%B3rdoba&ub=false&aprob=0.0&nprob=1.0&qc=true"
    #"https://www.paginasamarillas.es/search/all-ac/all-ma/cordoba/all-is/villa-del-rio/all-ba/all-pu/all-nc/1?what=gestiones+alarife&where=villa+del+r%C3%ADo&ub=false&aprob=0.5395485273896473&nprob=0.4604514726103527&qc=true"
    #url = "https://www.paginasamarillas.es/search/all-ac/all-ma/cordoba/all-is/cordoba/all-ba/all-pu/all-nc/1?what=mercadona&where=C%C3%B3rdoba&ub=false&aprob=0.0&nprob=1.0&qc=true"


    body = {
        "url":url,
        "httpResponseBody": True,
        "geolocation": "ES",
        "httpRequestMethod": "POST",
    }
    # Variable para almacenar los results
    results={
        "Encontrado": None,
        "Nombre": None,
        "Dirección": None,
        "Provincia": None,
        "Localidad": None,
        "Similaridad_direccion": None,
        "Error": None
    }

   
    try:

        response=requests.post("https://api.zyte.com/v1/extract", auth=(ZYTE_APIKEY, ""), json=body)
        print(f"Solicitud: {body}")
        print(f"Código de estado HTTP: {response.status_code}")
        if response.status_code!=200:
            results["Error"]= "Ha habido un problema con la API"
            return results

       # print(response)
        #print(response.json())
        content=response.json()

        html_content: bytes = b64decode(
        content["httpResponseBody"])
        
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        # Encontrar todos los elementos que contienen la información de los negocios
        businesses = soup.find_all('div', class_='listado-item')

        # Iterar sobre cada negocio y extraer la información
        for business in businesses:
                
            # Extraer el nombre del negocio
            data_analytics = business.get('data-analytics', '')

            try:
                name = data_analytics.split('"name":"')[1].split('"')[0]
            except IndexError:
                name = ""  # Si no existe, guardar un string vacío

            # Extraer la provincia
            try:
                found_province = data_analytics.split('"province":"')[1].split('"')[0]
            except IndexError:
                found_province = ""  

            # Extraer la localidad
            locality_element = business.find('span', itemprop="addressLocality")
            #print(locality_element.text)
            locality = locality_element.text.strip() if locality_element else ""  # Si no existe, guardar vacío

            # Extraer la dirección (calle + codigo postal)
            street = business.find('span', itemprop="streetAddress")
            postal_code = business.find('span', itemprop="postalCode")
            print(street.text)
            print(postal_code.text)
            address = (street.text.strip() +" "+ postal_code.text.strip()) if (street or postal_code) else ""  # Si no existe, guardar vacío
            
            print(f"Nombre del negocio: {name}")
            print(f"Dirección encontrada: {address}")
            print(f"Localidad encontrada: {locality}")
            print(f"Provincia encontrada: {found_province}")

            # Lógica para determinar si el negocio ha sido encontrado o no
            # Consideramos que:
            #    - La dirección debe similar en al menos un 85% para que sea válida. Contemplamos que existan algunos mismatch.
            #    (Esto sería lo ideal, pero como el sistema no está optimizado para franquicias, no está implementada en esta versión
            #    la comprobación de similaridad de dirección para determinar si el negocio ha sido encontrado.)
            #    - Si el nombre, la dirección, la localidad y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la localidad coinciden, es válido.
            # Si se considera válido, se guardarán todos los datos, independientemente de si coinciden o no,
            # y posteriormente se etiquetarán como inconsistentes

            name_match= True if nombre_negocio.lower() in name.lower() else False
            locality_match= True if ciudad.lower() in locality.lower() else False
            province_match= True if province.lower() in found_province.lower() else False
            address_similarity=similarity(direccion,address)
            direccion_match=True if address_similarity>=85.00 else False

            if(name_match and (province_match or locality_match)):
                # Guardar en el diccionario si coincide
                results = {
                    "Encontrado": "Si",
                    "Nombre": name , 
                    "Dirección": address, 
                    "Provincia": found_province,
                    "Localidad": locality,
                    "Similaridad_direccion": address_similarity,
                    "Error":None
                }    
                return results 
               
        
        results["Encontrado"]="No" 

    except requests.RequestException as e:
        results["Error"]= f"Error en la solicitud: {e}"
        print(f"Error en la solicitud: {e}")
    except requests.exceptions.Timeout:
        results["Error"]= f"Error: La solicitud ha excedido el tiempo de espera."
    except requests.exceptions.ConnectionError:
        results["Error"]= f"Error: Problema de conexión, la URL podría estar bloqueada o caída."
    return results

# Ejemplo de uso
"""nombre = "Gestiones Alarife"
ciudad = "Villa del río"
provincia="Córdoba"
direccion="Calle Simón Carpintero, 1 NAVE 20B, 14014"
existe = search_for_business_paginas_amarillas(nombre, ciudad, provincia, direccion)
print(existe)
"""

import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from backend.ingestion.scraping.normalizations import similarity,normalize_URL_Firmania
from base64 import b64decode

ZYTE_APIKEY=os.environ.get("ZYTE_APIKEY")


def search_for_business_firmania(business_name, city, province,address,page=1, results=None):
    print("\n[---------------SCRAPEANDO FIRMANIA--------------]")

    # Inicializar resultados si es la primera llamada
    if results is None:
        results = {
            "Encontrado": "No",
            "Nombre": None,
            "Dirección": None,
            "Provincia": None,
            "Localidad": None,
            "Similaridad_direccion": 0,
            "Error": None
        }

    # Formatear la URL de búsqueda en Firmania con codificación URL
    formated_name = normalize_URL_Firmania(business_name)
    formated_province = normalize_URL_Firmania(province)
    body = {
        "url":f"https://www.firmania.es/search?what={formated_name}&where={formated_province}&page={page}",
        "httpResponseBody": True,
        "geolocation": "ES",
        "httpRequestMethod": "POST",
    }
    
    #https://firmania.es/search?what=Mercadona&where=C%C3%B3rdoba&page=2
    #https://firmania.es/search?what=Mercadona&where=C%C3%B3rdoba%2C+C%2F+Santa+Rosa%2C+10%2C+C%C3%B3rdoba%2C+14006
    
    try:
        #response = requests.get(url, headers=headers, timeout=15)
        response=requests.post("https://api.zyte.com/v1/extract", auth=(ZYTE_APIKEY, ""), json=body)
        print(f"Solicitud: {body}")
        print(f"Código de estado HTTP: {response.status_code}")
        if response.status_code != 200:
            results["Error"]= "Ha habido un problema con la API"
            return results

        #print(response)
        content=response.json()

        html_content: bytes = b64decode(
        content["httpResponseBody"])
        #print(content)
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        #print(soup)


        # Buscar el bloque principal de resultados
        bloque_resultados = soup.find("div", class_="lg:grid lg:grid-cols-2 lg:gap-8 pt-4")
          
        if not bloque_resultados:
            print("No se encontró el bloque de resultados.")
            return results
            
        # Buscar todos los enlaces dentro del bloque
        enlaces = bloque_resultados.find_all("a", class_="company-tracking-list")
        last_page = bloque_resultados.find("a",title="Ir a la última página")
        num_pags = int(parse_qs(urlparse(last_page.get('href')).query)['page'][0]) if last_page else 1

            
        for enlace in enlaces:
            h3_element = enlace.find("h3", class_="company-name")
            if h3_element and business_name.lower() in h3_element.text.lower():
                name=h3_element.text
                address_element = enlace.find("p",class_="address")
                if address_element:
                    #print(address_element)
                    texto=address_element.text.strip()  
                    partes = [p.strip() for p in texto.split(",")]

                    # La localidad es la penúltima parte
                    locality = partes[-2]

                    # La dirección es todo lo anterior a la localidad
                    found_address = ", ".join(partes[:-2])

                print(f"Nombre encontrado {name}")
                print(f"Localidad encontrada {locality}")
                print(f"Dirección encontrada {found_address}")
            

            # Lógica para determinar si el negocio ha sido encontrado o no
            # Consideramos que:
            #    - La dirección debe similar en al menos un 85% para que sea válida. Contemplamos que existan algunos mismatch.
            #    (Esto sería lo ideal, pero como el sistema no está optimizado para franquicias, no está implementada en esta versión
            #    la comprobación de similaridad de dirección para determinar si el negocio ha sido encontrado.)
            #    - Si el nombre, la dirección, la localidad y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la provincia coinciden, es válido. (En el caso de Firmania, no existe 
            #     un campo dedicado a la provincia.)
            #    - Si el nombre, la dirección y la localidad coinciden, es válido.
            # Si se considera válido, se guardarán todos los datos, independientemente de si coinciden o no,
            # y posteriormente se etiquetarán como inconsistentes

                name_match= True if business_name.lower() in name.lower() else False
                #print(name_match)
                locality_match= True if city.lower() in locality.lower() else False
                #print(locality_match)
                #province_match= True if provincia.lower() in province.lower() else False
                address_similarity=similarity(address,found_address)
                direction_match=True if address_similarity>=85.00 else False
                #print(direction_match)


                #if(name_match and direction_match and locality_match):
                if(name_match and locality_match):
                        # Guardar en el diccionario si coincide
                    results={
                        "Encontrado": "Si",
                        "Nombre": name,
                        "Dirección": found_address,
                        "Provincia": province,
                        "Localidad": locality,
                        "Similaridad_direccion": address_similarity,
                        "Error": None
                    }
                    return results    
            
        if page < num_pags:
            return search_for_business_firmania(
                business_name, city, province, address, page + 1, results
            )
            
    except requests.RequestException as e:
        results["Error"]= f"Error en la solicitud: {e}"
        print(f"Error en la solicitud: {e}")
    except requests.exceptions.Timeout:
        results["Error"]= f"Error: La solicitud ha excedido el tiempo de espera."
    except requests.exceptions.ConnectionError:
        results["Error"]= f"Error: Problema de conexión, la URL podría estar bloqueada o caída."
        
    return results  # Si no se encuentra, devolver False

# Ejemplo de uso
"""nombre = "Dobuss"
city = "Córdoba"
province = "Córdoba"
address= "C/ Ingeniero Barbudo"
existe = search_for_business_firmania(nombre,city,province,address)
print(existe)
"""
import requests
import os
from bs4 import BeautifulSoup
from backend.ingestion.scraping.normalizations import *
from base64 import b64decode

ZYTE_APIKEY=os.environ.get("ZYTE_APIKEY")

def buscar_negocio_habitissimo(nombre_negocio, city,province,address):
    print("\n[---------------SCRAPEANDO HABITISSIMO--------------]")
    # Formatear la URL de búsqueda según Habitissimo
    nombre_formateado = nombre_negocio.replace(" ", "-").lower()

    body = {
        "url":f"https://www.habitissimo.es/pro/{nombre_formateado}",
        "httpResponseBody": True,
        "geolocation": "ES",
        "httpRequestMethod": "POST",
    }

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
        if response.status_code != 200:
            results["Error"]= "Ha habido un problema con la API"
            return results

        content=response.json()
        #print(content)

        html_content: bytes = b64decode(
        content["httpResponseBody"])
        #print(html_content)

        if html_content is None:
            results={
                "Encontrado": "No",
                "Nombre": None,
                "Dirección": None,
                "Provincia": None,
                "Localidad": None,
                "Similaridad_direccion": None,
                "Error": None
                }  
            return results
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        #print(soup)
        
        # Para depuración
        #with open('archivo.txt', 'a') as archivo:
            # Agrega el texto al final del archivo
            #archivo.write(response.text)

    
        # Buscar el nombre del negocio en el h1 con class "business-name" (nombre del negocio)
        business_name_tag = soup.find("h1", class_="business-name")
        name = business_name_tag.text.strip() if business_name_tag else ""  # Si no existe, guardar vacío para evitar errores
        print(f"Nombre del negocio encontrado: {name}")
            

        # Buscar la meta con itemprop="addressLocality" (localidad)
        meta_tag_locality = soup.find("meta", itemprop="addressLocality")
        locality = meta_tag_locality["content"] if meta_tag_locality and "content" in meta_tag_locality.attrs else ""
        print(f"Localidad encontrada: {locality}")
            
                
        # Buscar la meta con itemprop="addressRegion" (provincia)
        meta_tag_province = soup.find("meta", itemprop="addressRegion")
        found_province = meta_tag_province["content"] if meta_tag_province and "content" in meta_tag_province.attrs else ""
        print(f"Localidad encontrada: {found_province}")

        
        # Buscar dirección
        address_container = soup.find("aside", id="business-sidebar-contact-info")
        if address_container:
            address_link = address_container.find("a")
            found_address=address_link.find("span").text.strip() if address_link else ""
        else:
            found_address=""
                

        # Lógica para determinar si el negocio ha sido encontrado o no
            # Consideramos que:
            #    - La dirección debe similar en al menos un 85% para que sea válida. Contemplamos que existan algunos mismatch.
            #    - Si el nombre, la dirección, la localidad y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la localidad coinciden, es válido.
            # Si se considera válido, se guardarán todos los datos, independientemente de si coinciden o no,
            # y posteriormente se etiquetarán como inconsistentes
                        
        name_match= True if nombre_negocio.lower() in name.lower() else False
        print(name_match)
        locality_match= True if city.lower() in locality.lower() else False
        print(locality_match)
        province_match= True if province.lower() in found_province.lower() else False
        print(province_match)
        address_similarity=similarity(address,found_address)
        direction_match=True if address_similarity>=85.00 else False
        print(direction_match)


        #if(name_match and direction_match and (locality_match or province_match)):
        if(name_match and (locality_match or province_match)):
            # Guardar en el diccionario si coincide
            results={
                "Encontrado": "Si",
                "Nombre": name,
                "Dirección": found_address,
                "Provincia": found_province,
                "Localidad": locality,
                "Similaridad_direccion": address_similarity,
                "Error": None
                }  
        else:
            results={
                "Encontrado": "No",
                "Nombre": name,
                "Dirección": found_address,
                "Provincia": found_province,
                "Localidad": locality,
                "Similaridad_direccion": address_similarity,
                "Error": None
                }  
        return results

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
ciudad = "Córdoba"
provincia="Córdoba"
direccion="Calle Santas Flora y María, 44 - Local y C/ Mirto, 7, 14012, Córdoba"
existe = buscar_negocio_habitissimo(nombre,ciudad,provincia,direccion)
print(existe)
"""
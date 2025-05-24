import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import unicodedata
from ingestion.scraping.normalizaciones import *
from base64 import b64decode


# Normalizar el texto para descomponer los caracteres acentuados y 
# filtra los caracteres para eliminar los diacríticos (tildes) y
# convierte a minúscula

def normalizar_texto(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn'
    ).lower()

def buscar_negocio_infoisinfo(nombre_negocio, locality, province,address):
    print("\n[---------------SCRAPEANDO INFO IS INFO--------------]")

    # Formatear la URL de búsqueda en InfoisInfo con codificación URL
    #nombre_formateado1 = urllib.parse.quote(nombre_negocio.replace(" ", ""))
    nombre_formateado1 = urllib.parse.quote(nombre_negocio)
    ciudad_formateada1 = normalizar_texto(locality)
    nombre_formateado2 = urllib.parse.quote(nombre_negocio.replace(" ", "+"))
    ciudad_formateada2 = urllib.parse.quote(locality.replace(" ", "+"))
     
    url1 = f"https://{ciudad_formateada1}.infoisinfo.es/busquedanombre/{nombre_formateado1}"
    #url2= f"https://www.infoisinfo.es/search/?q={nombre_formateado2}&ql={ciudad_formateada2}"
    #url2 = f"https://search/?{ciudad_formateada1}.infoisinfo.es/busquedanombre/{nombre_formateado1}"
    posibles_url={url1}

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
        body = {
        "url":url1,
        "httpResponseBody": True,
        "geolocation": "ES",
        "httpRequestMethod": "POST",
        }
            
        response=requests.post("https://api.zyte.com/v1/extract", auth=("87310b733f3548a297ebffb3ffb0594e", ""), json=body)
        print(f"Solicitud: {body}")
        print(f"Código de estado HTTP: {response.status_code}")
        if response.status_code != 200:
            results["Error"]= "Ha habido un problema con la API"
            return results

        #print(response)
        #print(response.json())
        content=response.json()

        html_content: bytes = b64decode(
        content["httpResponseBody"])
        #print(content)
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        #print(soup)
            
        # Buscar la estructura deseada
        results_wrapper = soup.find("div", class_="results-wrapper ES pull-right")
        if not results_wrapper:
            results["Error"]="No se encontró la lista de empresas"
            return results
        
        """content_wrapper = results_wrapper.find("div", class_="content-wrapper adjust-height clearfix")
        if not content_wrapper:
            print("No se encontró 'content-wrapper'")
            return False"""
        
        company_list = results_wrapper.find("ul")
        if not company_list:
            results["Error"]= f"No se encontró la lista de empresas"
            return results
        
        companies = company_list.find_all("li", class_="company card eventa")

        # Inicialización para evitar errores
        business_name=""
        city=""
        found_province=""
        found_address=""
        
        for company in companies:
            title = company.find("h2", class_="title")
            address_tag= company.find("p", class_="address")

            if title:
                business_name = title.find("span", class_="title-com").text.strip()
            if address_tag:
                city = address_tag.find("span", class_="addressLocality").text.strip()
                found_province = address_tag.find("span", class_="addressState").text.strip()
                found_address = address_tag.find("span", class_="streetAddress").text.strip()

        
                #if found_province:
                    #print(f"Negocio encontrado: {business_name} en {city}, {found_province}")
                    #if nombre_negocio.lower() in business_name.lower() and ciudad.lower() in city.lower() and found_province==province:
                    #   return True
                #else: 
                    #print(f"Negocio encontrado: {business_name} en {city}")
                    #if nombre_negocio.lower() in business_name.lower() and ciudad.lower() in city.lower():
                        #return True
                    
            # Lógica para determinar si el negocio ha sido encontrado o no
            # Consideramos que:
            #    - La dirección debe similar en al menos un 85% para que sea válida. Contemplamos que existan algunos mismatch.
            #    - Si el nombre, la dirección, la localidad y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la localidad coinciden, es válido.
            # Si se considera válido, se guardarán todos los datos, independientemente de si coinciden o no,
            # y posteriormente se etiquetarán como inconsistentes
                    
            name_match= True if nombre_negocio.lower() in business_name.lower() else False
            print(name_match)
            locality_match= True if locality.lower() in city.lower() else False
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
                    "Nombre": business_name,
                    "Dirección": found_address,
                    "Provincia": found_province,
                    "Localidad": locality,
                    "Similaridad_direccion": address_similarity,
                    "Error": None
                    }
                return results
            else:
                results={
                    "Encontrado": "No",
                    "Nombre": business_name,
                    "Dirección": found_address,
                    "Provincia": found_province,
                    "Localidad": locality,
                    "Similaridad_direccion": address_similarity,
                    "Error": None
                    }                         

    except requests.RequestException as e:
        results["Error"]= f"Error en la solicitud: {e}"
        print(f"Error en la solicitud: {e}")
        #return False  # Manejo de errores en la solicitud
    except requests.exceptions.Timeout:
        results["Error"]= f"Error: La solicitud ha excedido el tiempo de espera."
    except requests.exceptions.ConnectionError:
        results["Error"]= f"Error: Problema de conexión, la URL podría estar bloqueada o caída."
    return results 

# Ejemplo de uso
"""nombre = "Dobuss"
ciudad = "Córdoba"
provincia="Córdoba"
direccion="C/ Ingeniero Barbudo"
existe = buscar_negocio_infoisinfo(nombre,ciudad,provincia,direccion)
print(existe)
print(f"El negocio '{nombre}' en '{ciudad}' {'EXISTE' if existe else 'NO EXISTE'} en InfoisInfo.")"""

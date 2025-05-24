import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import unicodedata
from normalizaciones import *

def normalizar_texto(texto):
    return urllib.parse.quote("+".join(texto.lower().split()))

def texto_minuscula(texto):
    # Normalizar el texto para descomponer los caracteres acentuados
    texto_normalizado = unicodedata.normalize('NFD', texto)
    
    # Filtrar los caracteres para eliminar los diacríticos (acentos)
    texto_sin_acentos = ''.join(
        c for c in texto_normalizado if unicodedata.category(c) != 'Mn'
    )
    
    # Sustituir espacios por guiones y convertir a minúscula
    texto_minuscula = texto_sin_acentos.replace(" ", "-").lower()
    
    return texto_minuscula


def buscar_negocio_paginas_amarillas(nombre_negocio, ciudad,provincia,direccion):
    # Formatear la URL de búsqueda en paginas_amarillas
    nombre_formateado = normalizar_texto(nombre_negocio)
    ciudad_formateada = normalizar_texto(ciudad)
    ciudad_minuscula= texto_minuscula(ciudad)
    provincia_minuscula=texto_minuscula(provincia)
    url = f"https://www.paginasamarillas.es/search/all-ac/all-ma/{provincia_minuscula}/all-is/{ciudad_minuscula}/all-ba/all-pu/all-nc/1?what={nombre_formateado}&where={ciudad_formateada}&ub=false&aprob=0.0&nprob=1.0&qc=true"
    #"https://www.paginasamarillas.es/search/all-ac/all-ma/cordoba/all-is/cordoba/all-ba/all-pu/all-nc/1?what=dobuss&where=C%C3%B3rdoba&ub=false&aprob=0.0&nprob=1.0&qc=true"
    #"https://www.paginasamarillas.es/search/all-ac/all-ma/cordoba/all-is/villa-del-rio/all-ba/all-pu/all-nc/1?what=gestiones+alarife&where=villa+del+r%C3%ADo&ub=false&aprob=0.5395485273896473&nprob=0.4604514726103527&qc=true"
    #url = "https://www.paginasamarillas.es/search/all-ac/all-ma/cordoba/all-is/cordoba/all-ba/all-pu/all-nc/1?what=mercadona&where=C%C3%B3rdoba&ub=false&aprob=0.0&nprob=1.0&qc=true"
    
    # Encabezados para imitar un navegador real
    headers = {
    "User-Agent": random.choice([
        # Chrome Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.89 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0",
        
        # Chrome MacOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.92 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
        
        # Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:112.0) Gecko/20100101 Firefox/112.0",
        
        # Edge Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.117 Safari/537.36 Edg/118.0.2088.76",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36 Edg/116.0.1938.81",
        
        # Safari MacOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.1 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.4 Safari/537.36",
    ]),
    "Accept-Language": "es-ES,es;q=0.9",
    "Referer": "https://www.google.com/"
    }

    body = {
        "cmd": "request.get",
        "url": url,
        "premiumProxy": "true",
        "automaticallySolveCaptchas": "true",
        "datadomeBypass": "true"
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

        response=requests.post("https://publisher.scrappey.com/api/v1?key=bwlharWADjbFDvuHe87GnUNflp6iUZ14Ar3VQdaFaKRDKD8mqXpAAF9a3GMz",json=body) #ocultar?
        print(f"Solicitud: {body}")
        print(f"Código de estado HTTP: {response.status_code}")
        if response.status_code!=200:
            results["Error"]= "Ha habido un problema con la API"
            return results
        
        content=response.json()
        print(content)
        verified=content["solution"]["verified"]
        if verified!=True:
            results["Error"]= "Ha habido algún problema con captchas"
            return results  # Ha habido algún problema con captchas
        else:
            status=content["solution"]["statusCode"]
            if status!= 200:
                results["Error"]= f"El código devuelto es: {status}"
                return results  # Si no carga bien la página, asumimos que no está
        
        html_content = content["solution"]["response"]
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        #print(soup)
        # Abre el archivo en modo adición ('a')
        #with open('archivo.txt', 'w') as archivo:
            # Agrega el texto al final del archivo
            #archivo.write(response.text)

        

        
         # Buscar el nombre del negocio en el h1 con class "business-name"
        """nombre_negocio_tag = soup.find("h1", class_="business-name")
        if nombre_negocio_tag:
            nombre_negocio_texto = nombre_negocio_tag.text.strip()
            print(f"Nombre del negocio encontrado: {nombre_negocio_texto}")
            
            # Verificar si el nombre del negocio coincide
            if nombre_negocio.lower() in nombre_negocio_texto.lower():
                print(f"El nombre del negocio coincide")

                # Buscar la meta con itemprop="addressLocality"
                meta_tag = soup.find("meta", itemprop="addressLocality")

                if meta_tag and "content" in meta_tag.attrs:
                    localidad = meta_tag["content"]
                    print(f"Localidad encontrada: {localidad}")
                else:
                    print("No se encontró la localidad.")
                if ciudad.lower() in localidad.lower():
                        return True

                # Buscar la ciudad en el span dentro de la sección de contacto
                contacto_span = soup.find("meta", itemprop_="addressLocality")
                if contacto_span:
                    direccion_texto = contacto_span.text.strip()
                    print(f"Dirección encontrada: {direccion_texto}")
                    
                    # Verificar si la ciudad coincide en la dirección
                    if ciudad.lower() in direccion_texto.lower():
                        return True"""                
                        
        # Encontrar todos los elementos que contienen la información de los negocios
        businesses = soup.find_all('div', class_='listado-item')

        # Iterar sobre cada negocio y extraer la información
        for business in businesses:
                
            # Extraer el nombre del negocio de forma segura
            data_analytics = business.get('data-analytics', '')

            try:
                name = data_analytics.split('"name":"')[1].split('"')[0]
            except IndexError:
                name = ""  # Si no existe, guardar un string vacío

            # Extraer la provincia de forma segura
            try:
                province = data_analytics.split('"province":"')[1].split('"')[0]
            except IndexError:
                province = ""  

            # Extraer la localidad de forma segura
            locality_element = business.find('span', itemprop="addressLocality")
            print(locality_element.text)
            locality = locality_element.text.strip() if locality_element else ""  # Si no existe, guardar vacío

            # Extraer la dirección (calle + codigo postal)
            street = business.find('span', itemprop="streetAddress")
            postal_code = business.find('span', itemprop="postalCode")
            print(street.text)
            print(postal_code.text)
            address = (street.text.strip() +" "+ postal_code.text.strip()) if (street or postal_code) else ""  # Si no existe, guardar vacío
            
            print(f"Nombre del negocio: {name}")
            print(f"Dirección encontrada: {address}")
            print(f"Ciudad: {locality}")
            print(f"Provincia: {province}")

            # Lógica para determinar si el negocio ha sido encontrado o no
            # Consideramos que:
            #    - La dirección debe similar en al menos un 85% para que sea válida. Contemplamos que existan algunos mismatch.
            #    - Si el nombre, la dirección, la localidad y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la localidad coinciden, es válido.
            # Si se considera válido, se guardarán todos los datos, independientemente de si coinciden o no,
            # y posteriormente se etiquetarán como inconsistentes

            name_match= True if nombre_negocio.lower() in name.lower() else False
            locality_match= True if ciudad.lower() in locality.lower() else False
            province_match= True if provincia.lower() in province.lower() else False
            address_similarity=similarity(direccion,address)
            direccion_match=True if address_similarity>=85.00 else False

            if(name_match and direccion_match and (province_match or locality_match)):
                # Guardar en el diccionario si coincide
                results = {
                    "Encontrado": "Sí",
                    "Nombre": name , 
                    "Dirección": address, 
                    "Provincia": province,
                    "Localidad": locality,
                    "Similaridad_direccion": address_similarity,
                }    
                return results 
               
        
        results["Encontrado"]="No" 
        

    except requests.RequestException as e:
        results["Error"]= f"Error en la solicitud: {e}"
        print(f"Error en la solicitud: {e}")
        #return False  # Manejo de errores en la solicitud
        #return results
    except requests.exceptions.Timeout:
        print("Error: La solicitud ha excedido el tiempo de espera.")
    except requests.exceptions.ConnectionError:
        print("Error: Problema de conexión, la URL podría estar bloqueada o caída.")

    return results
    #return False  # Si no se encuentra, devolver False

# Ejemplo de uso
nombre = "Gestiones Alarife"
ciudad = "Villa del río"
provincia="Córdoba"
direccion="Calle Simón Carpintero, 1 NAVE 20B, 14014"
existe = buscar_negocio_paginas_amarillas(nombre, ciudad, provincia, direccion)
print(existe)
#print(f"El negocio '{nombre}' en '{ciudad}, {provincia}' {'EXISTE' if existe else 'NO EXISTE'} en paginas_amarillas.")


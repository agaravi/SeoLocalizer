import requests
import re
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import unicodedata
from normalizaciones import *


def normalizar_texto_suma(texto):
    return urllib.parse.quote("+".join(texto.lower().split()))

def separar_palabras(texto):
    palabras = texto.split()  # Divide el nombre en palabras usando espacios
    return palabras if len(palabras) > 1 else [texto]

def texto_minuscula(texto):
    # Normalizar el texto para descomponer los caracteres acentuados
    texto_normalizado = unicodedata.normalize('NFD', texto)
    
    # Filtrar los caracteres para eliminar los diacríticos (acentos)
    texto_sin_acentos = ''.join(
        c for c in texto_normalizado if unicodedata.category(c) != 'Mn'
    )
    
    # Sustituir espacios por guiones y convertir a minúscula
    texto_minuscula = texto_sin_acentos.replace(" ", "-").lower()
    
    return urllib.parse.quote(texto_minuscula)

def sin_acentos(texto):
    texto_normalizado = unicodedata.normalize('NFD', texto)
    
    # Filtrar los caracteres para eliminar los diacríticos (acentos)
    texto_sin_acentos = ''.join(
        c for c in texto_normalizado if unicodedata.category(c) != 'Mn'
    )
    return texto_sin_acentos


def buscar_con_keyword(keyword,tipo_negocio, nombre_negocio, localidad, province):
    # Formatear la URL de búsqueda en paginas_amarillas
    nombre_formateado = nombre_negocio.replace(" ", "-").lower()
    #print(nombre_formateado)
    localidad_formateada = normalizar_texto_suma(localidad)
    #print(localidad_formateada)
    localidad_minuscula= texto_minuscula(localidad)
    #print(localidad_minuscula)
    province_minuscula=texto_minuscula(province)
    #print(provincia_minuscula)
    tipo_negocio_minuscula=texto_minuscula(tipo_negocio)
    #print(tipo_negocio_minuscula)

#https://www.paginasamarillas.es/search/salon-de-u%C3%B1as/all-ma/cordoba/all-is/cordoba/all-ba/all-pu/all-nc/1?co=Wow!nails
    body = {
        "url": f"https://www.paginasamarillas.es/search/{tipo_negocio_minuscula}/all-ma/{province_minuscula}/all-is/{localidad_minuscula}/all-ba/all-pu/all-nc/1?co={keyword}"
    }
    #url = "https://www.paginasamarillas.es/search/gasolinera/all-ma/cordoba/all-is/villa-del-rio/all-ba/all-pu/all-nc/1?co=Repsol"
    # Encabezados para imitar un navegador real
    """headers = {
        "User-Agent": random.choice([
        # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        # Chrome MacOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        # Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        ]),
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/"
    }"""
        
    try:
        response=requests.post("https://n8n.tfgiiaga.shop/webhook/scrape-url",json=body) #ocultar?
        print(f"URL solicitada: {body}")
        #response = requests.get(url, headers=headers, timeout=10)
        print(f"Código de estado HTTP: {response.status_code}")
                
        # Espera aleatoria para evitar detección
        time.sleep(random.uniform(2, 10))
              
        if response.status_code != 200:
            return False  # Si no carga bien la página, asumimos que no está
               
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Abre el archivo en modo adición ('a')
        #with open('archivo.txt', 'w') as archivo:
            # Agrega el texto al final del archivo
            #archivo.write(response.text)
                                
        # Encontrar el mensaje de "no encontrado" que aparece cuando no se encuentra el negocio
        errors = soup.find('div', class_='mensaje-info2')
        #print(errors)
        if errors:
            errors_text=errors.find('h2')
            if errors_text:
                print(errors_text.text)
                #for palabra in keyword:
                if keyword.lower() in errors_text.text.lower():            
                        #print("Hola")
                        if "no tenemos resultados para la búsqueda" in errors_text.text:
                            #print("Encontrado2")
                            if localidad.lower() in errors_text.text.lower():
                                #print("Encontrado3")
                                print("Se ha encontrado un mensaje de \"negocio no encontrado\" pero eso no significa nada. Sigo buscando...")
                                #return False

        # Encontrar todos los elementos que contienen la información de los negocios
        businesses = soup.find_all('div', class_='listado-item')

        # Iterar sobre cada negocio y extraer la información
        for business in businesses:
            # Extraer el nombre del negocio
            name = business.get('data-analytics', '').split('"name":"')[1].split('"')[0]
            # Extraer la provincia (provincia)
            found_province = business.get('data-analytics', '').split('"province":"')[1].split('"')[0]
            # Buscar la etiqueta <a> con el enlace a la direccion
            link = business.find("a", href=True)
            if link:
                url_route = link["href"]
                print("----------------------------------------------")
                print(f"URL encontrada: {url_route}")

                # Usar una expresión regular para extraer la localidad (primer segmento después de '/f/')
                match = re.search(r'/f/([^/]+)/', url_route)
                            
                if match:
                    found_locality = match.group(1)
                    # Imprimir la información
                    print(f"Nombre del negocio: {name}")
                    print(f"Localidad extraída: {found_locality}")
                    print(f"Provincia: {found_province}")

                    if nombre_negocio in name:
                    #if keyword in name:
                        print("Nombre encontrado")
                        if localidad_minuscula==found_locality.lower():
                            print("Localidad coincide")
                            if province_minuscula==texto_minuscula(found_province):
                                print("Provincia coincide")
                                return True
                    else:
                        print("No se encontró nada.")
                                #return False
                else:
                    print("No se encontró enlace en el HTML.")
                        #return False


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
                        
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return False  # Manejo de errores en la solicitud
    except requests.exceptions.Timeout:
        print("Error: La solicitud ha excedido el tiempo de espera.")
    except requests.exceptions.ConnectionError:
        print("Error: Problema de conexión, la URL podría estar bloqueada o caída.")

    print(f"Después de analizar la página entera no se ha encontrado el negocio por la keyword {keyword}")


def buscar_negocio_paginas_amarillas2(tipo_negocio, nombre_negocio, localidad, province):
    print("\n[---------------SCRAPEANDO PÁGINAS AMARILLAS---------------]")

    palabras_negocio = separar_palabras(nombre_negocio)
    #print(palabras_negocio)
    palabras_clave=separar_palabras(tipo_negocio)
    #print(palabras_clave)

    if palabras_negocio != nombre_negocio:
        #Si el nombre del negocio tiene más de una palabra, por ejemplo "Gasolinera Repsol" hace 3 búsquedas: una por "Gasolinera", otra por "Repsol" y otra por "Gasolinera Repsol"
        for keyword in palabras_negocio:
            if keyword not in palabras_clave:
                print("-----------------------------------------------------------------------------------------------")
                print(f"Buscando por keyword {keyword}")
                if buscar_con_keyword(keyword,tipo_negocio, nombre_negocio, localidad, province)==True:
                    return True
        
    print("-----------------------------------------------------------------------------------------------")
    #Buscar por el nombre completo introducido
    print(f"Buscando con keyword {nombre_negocio}")
    return buscar_con_keyword(nombre_negocio,tipo_negocio, nombre_negocio, localidad, province)
        
    #return False  # Si no se encuentra, devolver False

# Ejemplo de uso
palabra_clave = "Gasolinera"
nombre = "Gasolinera Repsol"
ciudad = "Villa del Río"
provincia="Córdoba"
existe = buscar_negocio_paginas_amarillas2(palabra_clave,nombre,ciudad,provincia)
("\n -----------------------------------------------------------------------------------------------")
print(f"El negocio '{nombre}' en '{ciudad}' {'EXISTE' if existe else 'NO EXISTE'} en Páginas Amarillas.")
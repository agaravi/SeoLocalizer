import requests
import os
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse, parse_qs
from backend.ingestion.scraping.normalizations import *
from base64 import b64decode

ZYTE_APIKEY=os.environ.get("ZYTE_APIKEY")



def buscar_negocio_firmania(nombre_negocio, city, province,address,page=1, results=None):
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
    nombre_formateado = urllib.parse.quote("-".join(nombre_negocio.lower().split()))
    provincia_formateada = urllib.parse.quote("-".join(province.lower().split()))
    body = {
        "url":f"https://www.firmania.es/search?what={nombre_formateado}&where={provincia_formateada}&page={page}",
        "httpResponseBody": True,
        "geolocation": "ES",
        "httpRequestMethod": "POST",
    }
    
    #https://firmania.es/search?what=Mercadona&where=C%C3%B3rdoba&page=2
    #https://firmania.es/search?what=Mercadona&where=C%C3%B3rdoba%2C+C%2F+Santa+Rosa%2C+10%2C+C%C3%B3rdoba%2C+14006
    
    # 2. Usar sesiones persistentes
    #session = requests.Session()
    #session.cookies.update({"cookie_consent": "true"})  # Simular cookies

    # Encabezados para imitar un navegador real
    """headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site"
    }
    proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }
    """
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
            if h3_element and nombre_negocio.lower() in h3_element.text.lower():
                name=h3_element.text
                address_element = enlace.find("p",class_="address")
                if address_element:
                    #print(address_element)
                    texto=address_element.text.strip()  # Extraer el texto de la etiqueta
                    # Separar por comas
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
            #    - Si el nombre, la dirección, la localidad y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la provincia coinciden, es válido.
            #    - Si el nombre, la dirección y la localidad coinciden, es válido.
            # Si se considera válido, se guardarán todos los datos, independientemente de si coinciden o no,
            # y posteriormente se etiquetarán como inconsistentes

                name_match= True if nombre_negocio.lower() in name.lower() else False
                print(name_match)
                locality_match= True if city.lower() in locality.lower() else False
                print(locality_match)
                #province_match= True if provincia.lower() in province.lower() else False
                address_similarity=similarity(address,found_address)
                direction_match=True if address_similarity>=85.00 else False
                print(direction_match)


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
            #time.sleep(50)
            return buscar_negocio_firmania(
                nombre_negocio, city, province, address, page + 1, results
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
existe = buscar_negocio_firmania(nombre,city,province,address)
print(existe)
print(f"El negocio '{nombre}' en '{city}' {'EXISTE' if existe else 'NO EXISTE'} en Firmania.")"""

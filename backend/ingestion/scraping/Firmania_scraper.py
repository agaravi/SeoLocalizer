import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
from urllib.parse import urlparse, parse_qs
from ingestion.scraping.normalizaciones import *


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
            "cmd": "request.get",
            "url": f"https://www.firmania.es/search?what={nombre_formateado}&where={provincia_formateada}&page={page}",
            "retries": 3,
            "premiumProxy": "true",
            #"requestType": "request",
            "automaticallySolveCaptchas": "true"
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
    for attempt in range(2):
        print(f"Intento {attempt + 1}/2")
        try:
            #response = requests.get(url, headers=headers, timeout=15)
            response=requests.post("https://publisher.scrappey.com/api/v1?key=bwlharWADjbFDvuHe87GnUNflp6iUZ14Ar3VQdaFaKRDKD8mqXpAAF9a3GMz",json=body) #ocultar?
            print(f"Solicitud: {body}")
            print(f"Código de estado HTTP: {response.status_code}")
            # Primero, verificamos si la API de Scrappey respondió correctamente (status_code 200)
            if response.status_code != 200:
                error_msg = f"Error en la API de Scrappey: Código {response.status_code}"
                print(error_msg)
                if attempt < 2 - 1:
                    print(f"Esperando 2 segundos antes de reintentar...")
                    time.sleep(2)
                    continue # Continúa al siguiente intento
                else:
                    results["Error"] = error_msg
                    return results # Si es el último intento y falla la API de Scrappey, retorna el error

        #print("Contenido HTML de la respuesta:")
        #print(response.text)  # Imprime todo el HTML de la respuesta para debugging        
        # Espera aleatoria para evitar detección
        #time.sleep(random.uniform(2, 10))

            content=response.json()
        #print(content)
        # Ahora, verificamos la respuesta dentro del JSON de Scrappey
            verified = content.get("solution", {}).get("verified")
            
            if verified is not True:
                # Scrappey no verificó la solución o hubo un error interno de Scrappey (ej. page.goto error)
                scrappey_error = content.get("error", "Error desconocido de Scrappey")
                error_msg = f"Problema con la solución de Scrappey (verified: {verified}, error: {scrappey_error})"
                print(error_msg)
                results["Error"] = error_msg # Guardar el error de Scrappey

                # Si el error es un problema de carga de página (como ERR_HTTP2_PROTOCOL_ERROR), reintenta
                #if "CODE-0031" in scrappey_error or "net::" in scrappey_error:
                if attempt < 2 - 1:
                        print(f"Esperando 2 segundos antes de reintentar...")
                        time.sleep(2)
                        continue # Continúa al siguiente intento
                else:
                        return results # Si es el último intento y falla, retorna el error
                #else:
                    # Otros errores de Scrappey que no se resuelven con reintentos de URL (ej. captchas persistentes)
                #    return results 
            else:
                # La solución de Scrappey fue verificada, ahora revisamos el statusCode de la página de destino
                status_code_target = content["solution"].get("statusCode")
                if status_code_target != 200:
                    error_msg = f"El código HTTP de la página de destino es: {status_code_target}"
                    print(error_msg)
                    if attempt < 2 - 1:
                        print(f"Esperando 2 segundos antes de reintentar...")
                        time.sleep(2)
                        continue # Continúa al siguiente intento
                    else:
                        results["Error"] = error_msg
                        return results # Último intento fallido, retorna el error

        
       
            html_content = content["solution"]["response"]
            soup = BeautifulSoup(html_content, "html.parser")
            print(soup)

            # Buscar el bloque principal de resultados
            bloque_resultados = soup.find("div", class_="lg:grid lg:grid-cols-2 lg:gap-8 pt-4")
            
            if not bloque_resultados:
                print("No se encontró el bloque de resultados.")
                return False
            
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

                        # Controlar que pasaría si no hay suficientes campos
                        # if len(partes) < 2:
                            #return address, None  # No hay suficiente información para separar

                    # La localidad es la penúltima parte
                        locality = partes[-2]

                        # La dirección es todo lo anterior a la localidad
                        found_address = ", ".join(partes[:-2])

                    print(name)
                    print(locality)
                    print(found_address)
            

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
            #return False  # Manejo de errores en la solicitud
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

import requests
from bs4 import BeautifulSoup
import time
import random
import urllib.parse
import unicodedata
from ingestion.scraping.normalizaciones import *

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

    # Encabezados para imitar un navegador real
    """headers = {
        "User-Agent": random.choice([
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        # Chrome MacOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.2845.110 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        # Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
        ]),
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/"
    }"""
    for attempt in range(2):
        print(f"Intento {attempt + 1}/2 para la URL: {url1}")
        try:
            body = {
                "cmd": "request.get",
                "url": url1,
                "retries": 3, 
                "premiumProxy": "true",       
                #"requestType": "request",
                "automaticallySolveCaptchas": "true"
            }
            
            response = requests.post("https://publisher.scrappey.com/api/v1?key=bwlharWADjbFDvuHe87GnUNflp6iUZ14Ar3VQdaFaKRDKD8mqXpAAF9a3GMz", json=body)
            
            print(f"URL solicitada: {body}")
            print(f"Código de estado HTTP de Scrappey: {response.status_code}")

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

            content = response.json()
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
                    #return results 
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

            """try:
            body={
                "cmd": "request.get",
                "url":url1,
                "retries": 3,
                "premiumProxy": "true",              
                "requestType": "request",
                "automaticallySolveCaptchas": "true"
            }
            #response = requests.get(url, headers=headers, timeout=10)
            response=requests.post("https://publisher.scrappey.com/api/v1?key=bwlharWADjbFDvuHe87GnUNflp6iUZ14Ar3VQdaFaKRDKD8mqXpAAF9a3GMz",json=body) #ocultar?
            print(f"URL solicitada: {body}")
            print(f"Código de estado HTTP: {response.status_code}")
            if response.status_code!=200:
                results["Error"]= "Ha habido un problema con la API"
                return results
            #print("Contenido HTML de la respuesta:")
            #print(response.text)  # Imprime todo el HTML de la respuesta para debugging        
            # Espera aleatoria para evitar detección
            #time.sleep(random.uniform(2, 10))

            content=response.json()
            print(content)

            #print(html_content)
            verified=content["solution"]["verified"]
            if verified!=True:
                results["Error"]= "Ha habido algún problema con captchas"
                return results  # Ha habido algún problema con captchas
            else:
                status=content["solution"]["statusCode"]
                if status!= 200:
                    results["Error"]= f"El código devuelto es: {status}"
                    return results  # Si no carga bien la página, asumimos que no está
            """
            html_content = content["solution"]["response"]
            # Parsear el HTML con BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            
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
                    break  
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
                    #time.sleep(2)                        

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
ciudad = "Córdoba"
provincia="Córdoba"
direccion="C/ Ingeniero Barbudo"
existe = buscar_negocio_infoisinfo(nombre,ciudad,provincia,direccion)
print(existe)
print(f"El negocio '{nombre}' en '{ciudad}' {'EXISTE' if existe else 'NO EXISTE'} en InfoisInfo.")"""

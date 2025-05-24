import requests
from bs4 import BeautifulSoup
import time
import random
from ingestion.scraping.normalizaciones import *

def buscar_negocio_habitissimo(nombre_negocio, city,province,address):
    print("\n[---------------SCRAPEANDO HABITISSIMO--------------]")
    # Formatear la URL de búsqueda en Habitissimo
    nombre_formateado = nombre_negocio.replace(" ", "-").lower()
    #ciudad_formateada = ciudad.replace(" ", "+")
    body = {
        "cmd": "request.get",
        "url": f"https://www.habitissimo.es/pro/{nombre_formateado}",
        "requestType": "request",
        "datadomeBypass": "true"
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
    
    # Encabezados para imitar un navegador real
    """headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]),
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.google.com/"
    }"""
    
    try:
        #response = requests.get(url, headers=headers, timeout=10)
        response=requests.post("https://publisher.scrappey.com/api/v1?key=bwlharWADjbFDvuHe87GnUNflp6iUZ14Ar3VQdaFaKRDKD8mqXpAAF9a3GMz",json=body) #ocultar?
        print(f"Solicitud: {body}")
        print(f"Código de estado HTTP: {response.status_code}")
        if response.status_code!=200:
            results["Error"]= "Ha habido un problema con la API"
            return results
        #print("Contenido HTML de la respuesta:")
        #print(response.text)  # Imprime todo el HTML de la respuesta para debugging        
        # Espera aleatoria para evitar detección
        #time.sleep(random.uniform(2, 10))

        content=response.json()
        #print(content)
        # Abre el archivo en modo adición ('a')
        #with open('archivo.txt', 'a') as archivo:
            # Agrega el texto al final del archivo
            #archivo.write(response.text)
        
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
        
        html_content = content["solution"]["response"]
        # Parsear el HTML con BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        #print(soup)
        
        # Buscar el nombre del negocio en el h1 con class "business-name" (nombre del negocio)
        business_name_tag = soup.find("h1", class_="business-name")
        if business_name_tag:
            name = business_name_tag.text.strip()
            print(f"Nombre del negocio encontrado: {name}")
            

        # Buscar la meta con itemprop="addressLocality" (localidad)
        meta_tag_locality = soup.find("meta", itemprop="addressLocality")

        if meta_tag_locality and "content" in meta_tag_locality.attrs:
            locality = meta_tag_locality["content"]
            print(f"Localidad encontrada: {locality}")
        else:
            print("No se encontró la locality.")
            
                
        # Buscar la meta con itemprop="addressRegion" (provincia)
        meta_tag_province = soup.find("meta", itemprop="addressRegion")

        if meta_tag_province and "content" in meta_tag_province.attrs:
            found_province = meta_tag_province["content"]
            print(f"Localidad encontrada: {found_province}")
        else:
            print("No se encontró la localidad.")
        
        # Buscar dirección
        address_container = soup.find("aside", id="business-sidebar-contact-info")
        address_link = address_container.find("a",)
        found_address=address_link.find("span").text.strip()

                

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
        #return False  # Manejo de errores en la solicitud
    except requests.exceptions.Timeout:
        results["Error"]= f"Error: La solicitud ha excedido el tiempo de espera."
    except requests.exceptions.ConnectionError:
        results["Error"]= f"Error: Problema de conexión, la URL podría estar bloqueada o caída."
    return results  # Si no se encuentra, devolver False

# Ejemplo de uso
"""nombre = "Gestiones Alarife"
ciudad = "Córdoba"
provincia="Córdoba"
direccion="Calle Santas Flora y María, 44 - Local y C/ Mirto, 7, 14012, Córdoba"
existe = buscar_negocio_habitissimo(nombre,ciudad,provincia,direccion)
print(existe)
print(f"El negocio '{nombre}' en '{ciudad}' {'EXISTE' if existe else 'NO EXISTE'} en Habitissimo.")"""

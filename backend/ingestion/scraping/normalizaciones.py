import re
import unicodedata
from difflib import SequenceMatcher

def normalize_name(name):
    """ Normaliza el nombre de una empresa eliminando palabras o abreviaturas comunes."""
    # Convertir el nombre a minúsculas para una comparación sin distinción de mayúsculas y minúsculas
    normalized_name = name.lower()

    # Define las palabras a eliminar.
    remove_words = [
        " s.l.", " s.l", " s.a.", " s.a",
        " c.b.", " c.b", " a.i.e.", " a.i.e",
        " sl", " sa", " cb", " aie",
        " sociedad limitada", " sociedad anonima",
        " y cia", " y compañia",
        " group", " grupo", " the ", " el ", " la ", " los ", " las ",
        " llc", " inc.", " inc", " corp.", " corp", " ltd.", " ltd"
    ]

    # Elimina las palabras de la lista
    for word in remove_words:
        normalized_name = normalized_name.replace(word, " ")

    normalized_name=re.sub(r'[.,;:()\-]', '', normalized_name)
    # Elimina múltiples espacios en blanco y espacios al inicio/final
    normalized_name = " ".join(normalized_name.split()).strip()

    # Opcional: Podrías querer capitalizar la primera letra de cada palabra
    # si el nombre final se va a mostrar al usuario.
    # return normalized_name.title() # Si quieres "Mi Empresa S.L." -> "Mi Empresa"

    return normalized_name

def normalize_address(address):
    # Lista de palabras irrelevantes a eliminar
    remove_words = {"calle", "avda", "avenida", "paseo", "carrer", "plaza", "camino", 
                            "carretera", "via", "nº", "local","num", "n", "c\\", "cl", "cr", "av"} 
       
    # Normalizar: eliminar tildes y pasar a minúsculas
    address = address.lower()
    address = unicodedata.normalize('NFD', address)
    address = ''.join(c for c in address if unicodedata.category(c) != 'Mn')
   
    # Eliminar caracteres especiales (comas, puntos, paréntesis, etc.)
    address = re.sub(r'[.,;:()\-]', ' ', address)

    # Normalizar números ordinales (1ºB → 1B)
    address = re.sub(r'\b(\d+)[º°]?\s*([a-zA-Z])\b', r'\1\2', address)

    # Convertir números escritos a dígitos
    reemplazos_numeros = {
        "primero": "1", "segundo": "2", "tercero": "3", "cuarto": "4", "quinto": "5",
        "sexto": "6", "septimo": "7", "octavo": "8", "noveno": "9", "decimo": "10"
    }
    for palabra, numero in reemplazos_numeros.items():
        address = re.sub(rf'\b{palabra}\b', numero, address)

    # Separar palabras y eliminar irrelevantes
    palabras = address.split()
    palabras_filtradas = [palabra for palabra in palabras if palabra not in remove_words]

    # Ordenar las palabras alfabéticamente para que el orden no afecte
    address_normalizada = " ".join(sorted(palabras_filtradas))

    return address_normalizada

def similarity(address1, address2):
    if address1 is None or address2 is None:
        return 0
    # Normalizar ambas addresses
    dir1_normalizada = normalize_address(address1)
    dir2_normalizada = normalize_address(address2)

    # Calcular la similitud
    similitud = SequenceMatcher(None, dir1_normalizada, dir2_normalizada).ratio()

    return round(similitud * 100, 2)  # Devolver porcentaje de similitud


#direccion1 = input("Dirección 1: ")
#direccion2 = input("Dirección 2: ")
#similaridad = similarity(direccion1, direccion2)
#print(normalizar_direccion(direccion1))
#print(normalizar_direccion(direccion2))
#print(f"Porcentaje de similitud: {similaridad}%")  # Output: ~100% si son equivalentes

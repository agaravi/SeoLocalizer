import re
import unicodedata
import urllib.parse
from difflib import SequenceMatcher

def lower_text(text):
    """Normalizar el texto para descomponer los caracteres acentuados"""
    normalized_text = unicodedata.normalize('NFD', text)
    
    # Filtrar los caracteres para eliminar los diacríticos (acentos)
    clean_text = ''.join(
        c for c in normalized_text if unicodedata.category(c) != 'Mn'
    )
    
    # Sustituir espacios por guiones y convertir a minúscula
    lower_text = clean_text.replace(" ", "-").lower()
    
    return lower_text

def normalize_URL_PaginasAmarillas(text):
    return urllib.parse.quote("+".join(text.lower().split()))

def normalize_URL_Firmania(text):
    return urllib.parse.quote("-".join(text.lower().split()))

def normalize_URL_InfoisInfo(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'
    ).lower()

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

    return normalized_name

def normalize_address(address):
    # Lista de palabras irrelevantes a eliminar
    remove_words = {"calle", "avda", "avenida", "paseo", "carrer", "plaza", "camino", 
                            "carretera", "via", "nº","s/n","local","num", "n", "c\\","c/", "cl", "cr", "av"} 
       
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

    # Ordenar las palabras alfabéticamente
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

    return round(similitud * 100, 2) 


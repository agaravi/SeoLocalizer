import requests
import json
import time
from processing.data_transformation import*
from business.models import Business,BusinessReview
#from processing.natural_language import *


def detect_language(text):
    """ Detecta el idioma de un texto usando LibreTranslate."""
    url = "https://n8n.tfgiiaga.shop/traductor/detect"
    payload = {
        "q": text
    }
    headers = {"Content-Type": "application/json"}
    try:
        time.sleep(0.2) #Para evitar sobrecargas
        response = requests.post(
            url,
            data=json.dumps(payload),  # convierte el dict a JSON string
            headers=headers
        )
        print(response.json())
        response.raise_for_status()  # Lanza error para códigos 4XX/5XX
        
        language = response.json()[0]['language']
        print(language)
        return language
    except requests.exceptions.RequestException as e:
        print(f"Error detectando idioma con LibreTranslate: {str(e)}")
        raise

def translate(text):
    url = "https://n8n.tfgiiaga.shop/traductor/translate"
    payload = {
        "q": text,
        "source": "en",
        "target": "es",
        "format": "text"
    }
    headers = {"Content-Type": "application/json"}
    try:
        time.sleep(0.2) # Para evitar sobrecargas
        response = requests.post(
            url,
            data=json.dumps(payload),  # convierte el dict a JSON string
            headers=headers
        )
        response.raise_for_status()  # Lanza error para códigos 4XX/5XX
        
        # Asumimos que la respuesta es JSON y contiene el campo 'translatedText'
        translated_text = response.json().get('translatedText', '')
        print(translated_text)
        return translated_text
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        raise


def translate_keywords(business:Business):
    """Función para sustituir las categorías de un objeto negocio por su versión traducida al español"""
    if business.categoria_principal is not None:
        categoria_principal=translate(business.categoria_principal)
    else:
        categoria_principal=None 
    if business.categorias_secundarias is not None:
        categorias_secundarias=business.categorias_secundarias 
        categorias_secundarias=[categoria.lower().strip().replace('_', ' ') for categoria in categorias_secundarias]
        categorias_secundarias=translate(categorias_secundarias)
    else:
        categorias_secundarias=None
    if business.categorias_no_incluidas!=[]:
        categorias_no_incluidas=business.categorias_no_incluidas 
        categorias_no_incluidas=[categoria.lower().strip().replace('_', ' ') for categoria in categorias_no_incluidas]
        categorias_no_incluidas=translate(categorias_no_incluidas)
    else:
        categorias_no_incluidas=[]
    if business.palabras_clave_en_resenas!=[]:
        palabras_clave_en_resenas=business.palabras_clave_en_resenas 
        palabras_clave_en_resenas=[categoria.lower().strip().replace('_', ' ') for categoria in palabras_clave_en_resenas]
        palabras_clave_en_resenas=translate(palabras_clave_en_resenas)
    else:
        palabras_clave_en_resenas=[]
    business.set_categories_translation(categoria_principal,categorias_secundarias,categorias_no_incluidas,palabras_clave_en_resenas)
    return

def translate_reviews(business:Business):
    business_reviews=business.get_reviews()
    business_translated_reviews=[]
    for review in business_reviews:
        cleaned_text=clean_text(review.texto)
        #if review.get_year_fecha_publicacion()<=2022:
        """Las reviews más antiguas de 2022 suelen encontrarse solo en inglés.
            Para reducir llamadas al servicio de traducción, distinguimos entre las reviews de
            años recientes, que 100% están en español y no las traducimos por tanto, y las antiguas."""
        if detect_language(cleaned_text)=="en":
            business_translated_reviews.append(translate(cleaned_text))
        elif detect_language(cleaned_text)=="es":
            business_translated_reviews.append(cleaned_text)
        #else:
            #business_translated_reviews.append(cleaned_text)
    #print(business_translated_reviews)
    business.set_reviews_translation(business_translated_reviews)
    return

"""def translate_reviews(main_business:Business,competitors:list[Business]):
    main_business_reviews=main_business.get_reviews()
    main_business_translated_reviews=[]
    for review in main_business_reviews:
        cleaned_text=clean_text(review.texto)
        #if review.get_year_fecha_publicacion()<=2022:
        Las reviews más antiguas de 2022 suelen encontrarse solo en inglés.
            Para reducir llamadas al servicio de traducción, distinguimos entre las reviews de
            años recientes, que 100% están en español y no las traducimos por tanto, y las antiguas.
        if detect_language(cleaned_text)=="en":
            main_business_translated_reviews.append(translate(cleaned_text))
        elif detect_language(cleaned_text)=="es":
            main_business_translated_reviews.append(cleaned_text)
        #else:
            #main_business_translated_reviews.append(cleaned_text)
    #print(main_business_translated_reviews)
    main_business.set_reviews_translation(main_business_translated_reviews)

    for competitor in competitors:
        competitor_reviews=competitor.get_reviews()
        #print("competitor reviews: ")
        #print(competitor_reviews)
        #print("\n\n")
        competitor_translated_reviews=[]
        for review in competitor_reviews:
            #if review.get_year_fecha_publicacion()<=2022:
                cleaned_text=clean_text(review.texto)
                if detect_language(cleaned_text)=="en":
                    competitor_translated_reviews.append(translate(cleaned_text))
                elif detect_language(cleaned_text)=="es":
                    competitor_translated_reviews.append(cleaned_text)
            #else:
                #competitor_translated_reviews.append(cleaned_text)
        #print(competitor_translated_reviews)
        competitor.set_reviews_translation(competitor_translated_reviews)
    return"""

#translate(["Hello","my","name","is","Alicia"])

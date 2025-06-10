from google.cloud import translate_v3
import os 
from backend.processing.data_transformation import clean_text
from backend.business.models import Business

CREDENTIALS="/etc/secrets/tfg-google-service-account-key.json"
PROJECT_NAME=os.environ.get("PROJECT_NAME")


##TRANSLATE BUSINESS PARA CENTRALIZAR
def translate_businesses(main_business:Business,competitors:list[Business]):
    print("-----Traduciendo keywords del negocio principal-----\n")
    translate_keywords_google(main_business)
    print("\n-----Traduciendo reviews del negocio principal-----\n")
    translate_reviews_google(main_business)
    for competitor in competitors:
        print("\n-----Traduciendo keywords del negocio ",competitor.nombre,"-----\n")    
        translate_keywords_google(competitor)
        print("\n-----Traduciendo reviews del negocio ",competitor.nombre,"-----\n")    
        translate_reviews_google(competitor)



def detect_language_google(text, project_id=PROJECT_NAME):
    """Detecta el idioma de un texto usando la API de Cloud Translation."""
    client = translate_v3.TranslationServiceClient.from_service_account_file(CREDENTIALS)
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"

    try:
        response = client.detect_language(
            request={"parent": parent, "content": text}
        )
        print(f"Idioma detectado: {response.languages[0].language_code}")
        return response.languages[0].language_code
    except Exception as e:
        print(f"Error detectando idioma con Google Cloud Translation: {e}")
        raise

def translate_google(text, target_language="es", source_language="en", project_id=PROJECT_NAME):
    """Traduce texto usando la API de Cloud Translation."""
    client = translate_v3.TranslationServiceClient.from_service_account_file(CREDENTIALS)
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"

    try:
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain", 
                "source_language_code": source_language,
                "target_language_code": target_language,
            }
        )
        translated_text = response.translations[0].translated_text
        print(f"Texto traducido: {translated_text}")
        return translated_text
    except Exception as e:
        print(f"Error traduciendo con Google Cloud Translation: {e}")
        raise

def translate_keywords_google(business: Business, project_id=PROJECT_NAME):
    """Función para sustituir las categorías de un objeto negocio por su versión traducida al español usando Google."""
    if business.categoria_principal is not None:
        categoria_principal = translate_google(business.categoria_principal, target_language="es", source_language="en", project_id=project_id)
    else:
        categoria_principal = None

    if business.categorias_secundarias is not None:
        categorias_secundarias = business.categorias_secundarias
        categorias_secundarias = [categoria.lower().strip().replace('_', ' ') for categoria in categorias_secundarias]
        categorias_secundarias_traducidas = [translate_google(cat, target_language="es", source_language="en", project_id=project_id) for cat in categorias_secundarias]
    else:
        categorias_secundarias = None
        categorias_secundarias_traducidas = None
    business.set_categories_translation(categoria_principal, categorias_secundarias_traducidas)
    return

def translate_reviews_google(business: Business, project_id=PROJECT_NAME):
    business_reviews = business.get_reviews()
    business_translated_reviews = []
    for review in business_reviews:
        if review.texto is not None:
            cleaned_text = clean_text(review.texto)
            try:
                translated_text = translate_google(cleaned_text, target_language="es", source_language="en", project_id=project_id)
                business_translated_reviews.append(translated_text)
            except Exception as e:
                print(f"Error al procesar la revisión: {e}")
                business_translated_reviews.append(cleaned_text) # En caso de error, conserva el texto original
    business.set_reviews_translation(business_translated_reviews)
    return
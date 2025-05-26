from google.cloud import translate_v3
import os 
from backend.processing.data_transformation import clean_text
from backend.business.models import Business

# Credenciales de Google Cloud (reemplaza con tu archivo de credenciales)
# Asegúrate de tener la variable de entorno GOOGLE_APPLICATION_CREDENTIALS configurada
# o proporciona la ruta al archivo JSON de tus credenciales.
# Ejemplo:
# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/credentials.json"
#CREDENTIALS = os.path.join(
#    os.path.dirname(os.path.abspath(__file__)),
#    "../config/tfg-google-service-account-key.json"
#)
CREDENTIALS="/etc/secrets/tfg-google-service-account-key.json"



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



def detect_language_google(text, project_id="trabajofingrado-453708"):
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

def translate_google(text, target_language="es", source_language="en", project_id="trabajofingrado-453708"):
    """Traduce texto usando la API de Cloud Translation."""
    client = translate_v3.TranslationServiceClient.from_service_account_file(CREDENTIALS)
    location = "global"
    parent = f"projects/{project_id}/locations/{location}"

    try:
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [text],
                "mime_type": "text/plain",  # Puedes ajustar esto si el texto es HTML
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

def translate_keywords_google(business: Business, project_id="trabajofingrado-453708"):
    """Función para sustituir las categorías de un objeto negocio por su versión traducida al español usando Google."""
    if business.categoria_principal is not None:
        categoria_principal = translate_google(business.categoria_principal, target_language="es", source_language="en", project_id=project_id)
    else:
        categoria_principal = None

    if business.categorias_secundarias is not None:
        categorias_secundarias = business.categorias_secundarias
        categorias_secundarias = [categoria.lower().strip().replace('_', ' ') for categoria in categorias_secundarias]
        # Google Translate API espera una lista de strings para traducir en lote
        categorias_secundarias_traducidas = [translate_google(cat, target_language="es", source_language="en", project_id=project_id) for cat in categorias_secundarias]
    else:
        categorias_secundarias = None
        categorias_secundarias_traducidas = None

    """if business.categorias_no_incluidas != []:
        categorias_no_incluidas = business.categorias_no_incluidas
        categorias_no_incluidas = [categoria.lower().strip().replace('_', ' ') for categoria in categorias_no_incluidas]
        categorias_no_incluidas_traducidas = [translate_google(cat, target_language="es", source_language="en", project_id=project_id) for cat in categorias_no_incluidas]
    else:
        categorias_no_incluidas = []
        categorias_no_incluidas_traducidas = []

    if business.palabras_clave_en_resenas != []:
        palabras_clave_en_resenas = business.palabras_clave_en_resenas
        palabras_clave_en_resenas = [categoria.lower().strip().replace('_', ' ') for categoria in palabras_clave_en_resenas]
        palabras_clave_en_resenas_traducidas = [translate_google(kw, target_language="es", source_language="en", project_id=project_id) for kw in palabras_clave_en_resenas]
    else:
        palabras_clave_en_resenas = []
        palabras_clave_en_resenas_traducidas = []

    if business.palabras_clave_en_resenas_competidores != []:
        palabras_clave_en_resenas_competidores = business.palabras_clave_en_resenas_competidores
        palabras_clave_en_resenas_competidores = [categoria.lower().strip().replace('_', ' ') for categoria in palabras_clave_en_resenas_competidores]
        palabras_clave_en_resenas_competidores_traducidas = [translate_google(kw, target_language="es", source_language="en", project_id=project_id) for kw in palabras_clave_en_resenas_competidores]
    else:
        palabras_clave_en_resenas_competidores = []
        palabras_clave_en_resenas_competidores_traducidas = []
    """
    business.set_categories_translation(categoria_principal, categorias_secundarias_traducidas)
    return

def translate_reviews_google(business: Business, project_id="trabajofingrado-453708"):
    business_reviews = business.get_reviews()
    business_translated_reviews = []
    for review in business_reviews:
        if review.texto is not None:
            cleaned_text = clean_text(review.texto)
            try:
                #language = detect_language_google(cleaned_text, project_id=project_id)
                #if language == "en":
                    translated_text = translate_google(cleaned_text, target_language="es", source_language="en", project_id=project_id)
                    business_translated_reviews.append(translated_text)
                #elif language == "es":
                    #business_translated_reviews.append(cleaned_text)
                #else:
                    # Si el idioma no es inglés ni español, puedes decidir qué hacer
                    # (traducir desde ese idioma a español, dejar el texto original, etc.)
                    #print(f"Idioma no soportado o no reconocido: {language}. Texto original: {cleaned_text}")
                    #business_translated_reviews.append(cleaned_text) # Opcional: traducir desde 'language' a 'es'
            except Exception as e:
                print(f"Error al procesar la revisión: {e}")
                business_translated_reviews.append(cleaned_text) # En caso de error, conserva el texto original
    business.set_reviews_translation(business_translated_reviews)
    return
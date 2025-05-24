#from utils.logger import logger


import re

def clean_text(text):
    # Elimina caracteres no traducibles (emojis y símbolos fuera del rango básico)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticonos
        u"\U0001F300-\U0001F5FF"  # símbolos y pictogramas
        u"\U0001F680-\U0001F6FF"  # transporte y mapas
        u"\U0001F1E0-\U0001F1FF"  # banderas
        u"\U00002700-\U000027BF"  # símbolos varios
        u"\U000024C2-\U0001F251"  # otros símbolos
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)




def transform_data(data):
    try:
        #logger.info("Transformando datos...")
        # Ejemplo: Limpiar y estructurar datos
        transformed_data = []
        for item in data:
            transformed_data.append({
                'name': item['name'].strip(),
                'address': item['address'].strip(),
                'rating': float(item['rating']) if item['rating'] != 'No disponible' else None
            })
        
        #logger.info(f"Datos transformados: {len(transformed_data)} registros.")
        return transformed_data
    except Exception as e:
        #logger.error(f"Error en la transformación de datos: {e}")
        return []
    

def transform_data_for_bigquery(data):
    # Helper para completitud
    checks = [
        data.get("displayName"),
        data.get("formattedAddress"),
        data.get("nationalPhoneNumber"),
        data.get("websiteUri"),
        data.get("photos"),
        data.get("rating"),
        data.get("userRatingCount"),
        data.get("regularOpeningHours"),
        data.get("primaryTypeDisplayName", {}).get("text"),
        data.get("types"),
        data.get("businessStatus"),
    ]
    completitud = sum(1 for item in checks if item)

    # Dirección postal
    postal = data.get("postalAddress", {})
    direccion = {
        "calle": ', '.join(postal.get("addressLines", [])),
        "ciudad": postal.get("locality"),
        "provincia": postal.get("administrativeArea"),
        "codigo_postal": postal.get("postalCode"),
        "pais": postal.get("regionCode")
    }

    # Reseñas
    reviews_data = data.get("reviews", [])
    reseñas = []
    for r in reviews_data:
        reseñas.append({
            "autor": r.get("authorAttribution", {}).get("displayName", ""),
            "texto": r.get("originalText", {}).get("text", ""),
            "fecha_publicacion": r.get("publishTime", ""),
            "fecha_relativa": r.get("relativePublishTimeDescription", ""),
            "valoracion": r.get("rating", None)
        })

    resultado = {
        "place_id": data.get("id"),
        "nombre": data.get("displayName", {}).get("text"),
        "direccion_completa": data.get("formattedAddress"),
        "telefono_nacional": data.get("nationalPhoneNumber"),
        "telefono_internacional": data.get("internationalPhoneNumber"),
        "website": data.get("websiteUri"),
        "n_fotos": len(data.get("photos", [])),
        "direccion": direccion["calle"],
        "ciudad": direccion["ciudad"],
        "provincia": direccion["provincia"],
        "codigo_postal": direccion["codigo_postal"],
        "pais": direccion["pais"],
        "valoracion_media": data.get("rating"),
        "n_valoraciones": data.get("userRatingCount"),
        "categoria_principal": data.get("primaryType"),
        "tipo_principal_nombre": data.get("primaryTypeDisplayName", {}).get("text"),
        "categorias_secundarias": data.get("types", []),
        "estado_negocio": data.get("businessStatus"),
        "sin_local_fisico": data.get("pureServiceAreaBusiness"),
        "horario_regular": str(data.get("regularOpeningHours", "")),
        "horario_secundario_regular": str(data.get("regularSecondaryOpeningHours", "")),
        "horario_actual": str(data.get("currentOpeningHours", "")),
        "horario_actual_secundario": str(data.get("currentSecondaryOpeningHours", "")),
        "perfil_completitud": completitud,
        "reseñas": reseñas
    }

    return resultado

import os
import requests

GOOGLE_PLACES_API_KEY=os.environ.get("GOOGLE_PLACES_API_KEY")


def get_google_places_data(nombre,ciudad,num_resultados):
    try:
        print("Obteniendo datos de Google Places API...")

        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "places.id"
        }
        textQuery={nombre+" "+ciudad,nombre+" cerca de "+ciudad,nombre+" España"}
        for query in textQuery:
            data = {
                "textQuery": query
            }

            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                print(f"Error en la solicitud: {response.status_code} - {response.text}")
                return []

            result = response.json()
            print(result)
            places = result.get("places", [])

            if not places:
                continue
            else:
                break
        
        if not places:
            print("No se encontraron resultados.")
            return []

        ids = [place.get("id") for place in places[:num_resultados]]
        print(f"{len(ids)} ID(s) encontrados:", ids)

        # Si solo se pidió 1 resultado, devolvemos solo ese valor
        if num_resultados == 1:
            return ids[0]

        return ids

    except Exception as e:
        print(f"Error al obtener datos de Google Places: {e}")
        return []

def get_details_main_place(id):
    try:
        url = f"https://places.googleapis.com/v1/places/{id}"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "id,displayName,formattedAddress,postalAddress,userRatingCount,rating,types,primaryType,primaryTypeDisplayName,"
            "businessStatus,pureServiceAreaBusiness,reviews,photos,currentOpeningHours,currentSecondaryOpeningHours,"
            "internationalPhoneNumber,nationalPhoneNumber,regularOpeningHours,regularSecondaryOpeningHours,websiteUri",
            "languageCode":"es",
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error en la solicitud: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        
        print("\n" + "="*60)
        print("INFORMACIÓN GENERAL DEL NEGOCIO")
        print("="*60)
        print(f"ID: {data.get('id', 'N/A')}")
        print(f"Nombre: {data.get('displayName', {}).get('text', 'N/A')}")
        print(f"Teléfono: {data.get('nationalPhoneNumber', 'N/A')} / {data.get('internationalPhoneNumber', 'N/A')}")
        print(f"Web: {data.get('websiteUri', 'N/A')}")
        print(f"Nº de fotos y vídeos: {len(data.get('photos', []))}")

        print("\n📍 DIRECCIÓN POSTAL")
        postal = data.get('postalAddress', {})
        print(f"Calle: {', '.join(postal.get('addressLines', [])) or 'N/A'}")
        print(f"Ciudad: {postal.get('locality', 'N/A')}")
        print(f"Provincia: {postal.get('administrativeArea', 'N/A')}")
        print(f"Código postal: {postal.get('postalCode', 'N/A')}")
        print(f"País: {postal.get('regionCode', 'N/A')}")
        print(f"Dirección completa: {data.get('formattedAddress', 'N/A')}")

        print("\n⭐ REPUTACIÓN")
        print(f"Valoración media: {data.get('rating', 'N/A')}")
        print(f"Nº de valoraciones: {data.get('userRatingCount', 'N/A')}")

        print("\n🏷️ CATEGORÍAS")
        print(f"Tipo principal: {data.get('primaryType', 'N/A')} - {data.get('primaryTypeDisplayName', {}).get('text', 'N/A')}")
        print(f"Tipos secundarios: {', '.join(data.get('types', [])) or 'N/A'}")

        print("\n📍 LOCALIZACIÓN / ESTADO")
        print(f"Estado del negocio: {data.get('businessStatus', 'N/A')}")
        print(f"Solo servicio sin local físico: {data.get('pureServiceAreaBusiness', 'N/A')}")

        print("\n⏰ HORARIOS")
        print(f"Horario regular: {data.get('regularOpeningHours', 'N/A')}")
        print(f"Horario secundario regular: {data.get('regularSecondaryOpeningHours', 'N/A')}")
        print(f"Horario actual: {data.get('currentOpeningHours', 'N/A')}")
        print(f"Horario actual secundario: {data.get('currentSecondaryOpeningHours', 'N/A')}")

        print("\n🗣️ RESEÑAS")
        reviews = data.get("reviews", [])
        if not reviews:
            print("No hay reseñas disponibles.")
        else:
            for i, review in enumerate(reviews, 1):
                autor = review.get("authorAttribution", {}).get("displayName", "Desconocido")
                texto = review.get("originalText", {}).get("text", "")
                fecha = review.get("publishTime", "Desconocida")
                fecha2 = review.get("relativePublishTimeDescription", "Desconocida")
                rating = review.get("rating", "Sin puntuación")
                print(f"\n🔸 Reseña {i}")
                print(f"Autor: {autor}")
                print(f"Fecha: {fecha} ({fecha2})")
                print(f"Puntuación: {rating}")
                print(f"Comentario: {texto}")

        return data


    except Exception as e:
        print(f"Error al obtener datos de Google Places: {e}")
        return []
    
def get_details_place(id):
    try:
        url = f"https://places.googleapis.com/v1/places/{id}"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "id,displayName,userRatingCount,rating,types,primaryType,primaryTypeDisplayName,"
            "reviews,photos,currentOpeningHours,currentSecondaryOpeningHours",
            "languageCode":"es"
        }
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Error en la solicitud: {response.status_code} - {response.text}")
            return []
        
        data = response.json()
        
        print("\n" + "="*60)
        print("INFORMACIÓN GENERAL DEL NEGOCIO")
        print("="*60)
        print(f"ID: {data.get('id', 'N/A')}")
        print(f"Nombre: {data.get('displayName', {}).get('text', 'N/A')}")
        print(f"Nº de fotos y vídeos: {len(data.get('photos', []))}")

        print("\n⭐ REPUTACIÓN")
        print(f"Valoración media: {data.get('rating', 'N/A')}")
        print(f"Nº de valoraciones: {data.get('userRatingCount', 'N/A')}")

        print("\n🏷️ CATEGORÍAS")
        print(f"Tipo principal: {data.get('primaryType', 'N/A')} - {data.get('primaryTypeDisplayName', {}).get('text', 'N/A')}")
        print(f"Tipos secundarios: {', '.join(data.get('types', [])) or 'N/A'}")

        print("\n🗣️ RESEÑAS")
        reviews = data.get("reviews", [])
        if not reviews:
            print("No hay reseñas disponibles.")
        else:
            for i, review in enumerate(reviews, 1):
                autor = review.get("authorAttribution", {}).get("displayName", "Desconocido")
                texto = review.get("originalText", {}).get("text", "")
                fecha = review.get("publishTime", "Desconocida")
                fecha2 = review.get("relativePublishTimeDescription", "Desconocida")
                rating = review.get("rating", "Sin puntuación")
                print(f"\n🔸 Reseña {i}")
                print(f"Autor: {autor}")
                print(f"Fecha: {fecha} ({fecha2})")
                print(f"Puntuación: {rating}")
                print(f"Comentario: {texto}")

        return data


    except Exception as e:
        print(f"Error al obtener datos de Google Places: {e}")
        return []
    
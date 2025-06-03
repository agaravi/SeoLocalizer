from google.cloud import language_v1
from google.cloud import language_v2 
from backend.business.models import Business


CREDENTIALS = "/etc/secrets/tfg-google-service-account-key.json"

def sentiment_analysis(main_business:Business,competitors:list[Business]):
    print("\n--------Negocio principal---------")
    main_business_translated_reviews=main_business.get_translated_reviews()
    print(main_business_translated_reviews)
    if main_business_translated_reviews:
        sentiment_main_business = analyze_reviews_sentiment(main_business_translated_reviews)
        main_top_positive, main_top_negative = analyze_keyword_sentiment(main_business_translated_reviews)
        entities_mentioned=extract_organizations_from_reviews(main_business_translated_reviews)
    #print(sentiment_main_business)
        main_business.set_sentiment_analysis(sentiment_main_business,main_top_positive,main_top_negative,entities_mentioned)
    for competitor in competitors:
        print("\n--------Competidor---------")
        competitor_translated_reviews=competitor.get_translated_reviews()
        print(competitor_translated_reviews)
        if competitor_translated_reviews is not None:
            sentiment_competitor = analyze_reviews_sentiment(competitor_translated_reviews)
            #print(sentiment_competitor)
            #top_positive,top_negative= analyze_keyword_sentiment(competitor_translated_reviews)
            #entities_mentioned_comp=extract_organizations_from_reviews(competitor_translated_reviews)
            competitor.set_sentiment_analysis(sentiment_competitor,None,None,None)
            #main_business.categorias_no_incluidas.extend(entities_mentioned_comp)

    sentiment_order=classify_sentiment_results(main_business,competitors)
    if main_business_translated_reviews:
        main_business.set_sentiment_order(sentiment_order)
        for competitor in competitors:
            if competitor.get_translated_reviews():
                competitor.set_sentiment_order(sentiment_order)
    #print(main_business)
    return

def analyze_sentiment(text):
    try:
        client = language_v1.LanguageServiceClient.from_service_account_file(CREDENTIALS)
        document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment
        
        print(f"Sentimiento analizado: Score={sentiment.score}, Magnitud={sentiment.magnitude}")
        return sentiment
    except Exception as e:
        print(f"Error en el análisis de sentimiento: {e}")
        return None
    
def analyze_reviews_sentiment(reviews):
    total_score = 0
    total_magnitude = 0
    valid_reviews_count = 0

    for review in reviews:
        sentiment = analyze_sentiment(review)
        if sentiment:
            total_score += sentiment.score
            total_magnitude += sentiment.magnitude
            valid_reviews_count += 1

    if valid_reviews_count > 0:
        average_score = total_score / valid_reviews_count
        average_magnitude = total_magnitude / valid_reviews_count
        print(f"\nResumen del sentimiento de las reseñas:")
        print(f"Puntuación promedio: {average_score}")
        print(f"Magnitud promedio: {average_magnitude}")
        return {"average_score": average_score, "average_magnitude": average_magnitude}
    else:
        print("\nNo se pudieron analizar reseñas válidas.")
        return None

def analyze_keyword_sentiment(reviews):
    """
    Analiza el sentimiento de las entidades o conceptos encontrados en las reseñas
    y devuelve las listas de palabras clave positivas y negativas con sus puntuaciones promedio.
    """
    client = language_v1.LanguageServiceClient.from_service_account_file(CREDENTIALS)
    positive_keywords = {}
    negative_keywords = {}

    for review in reviews:
        document = language_v1.Document(content=review, type=language_v1.Document.Type.PLAIN_TEXT)
        response = client.analyze_entity_sentiment(
            request={"document": document}
        )
        #print(response.json())

        for entity in response.entities:
            sentiment_score = entity.sentiment.score
            keyword = entity.name.lower()  # Convertir a minúsculas para agrupar

            if sentiment_score > 0.2:  # Umbral para considerar positivo
                if keyword in positive_keywords:
                    positive_keywords[keyword]["sum"] += sentiment_score
                    positive_keywords[keyword]["count"] += 1
                else:
                    positive_keywords[keyword] = {"sum": sentiment_score, "count": 1}
            elif sentiment_score < -0.2:  # Umbral para considerar negativo
                if keyword in negative_keywords:
                    negative_keywords[keyword]["sum"] += sentiment_score
                    negative_keywords[keyword]["count"] += 1
                else:
                    negative_keywords[keyword] = {"sum": sentiment_score, "count": 1}

    # Calcular la puntuación promedio
    avg_positive = {k: v["sum"] / v["count"] for k, v in positive_keywords.items()}
    avg_negative = {k: v["sum"] / v["count"] for k, v in negative_keywords.items()}

    # Ordenar por puntuación (más positivo/negativo primero)
    top_positive = sorted(avg_positive.items(), key=lambda item: item[1], reverse=True)
    top_negative = sorted(avg_negative.items(), key=lambda item: item[1])

    return top_positive[:10], top_negative[:10]# Devolver las 10 principales

# Ejemplo de uso (asumiendo que tienes las reseñas traducidas en una lista)
# top_positivas, top_negativas = extraer_palabras_clave_con_sentimiento(main_business.reviews_traducidas)
# print("Palabras clave positivas:", top_positivas)
# print("Palabras clave negativas:", top_negativas)

def extract_organizations_from_reviews(reviews: list[str]) -> list:
    """
    Extrae los nombres de las organizaciones mencionadas en una lista de reseñas,
    sin incluir duplicados.

    Args:
        reviews (list[str]): Una lista de textos de reseñas.

    Returns:
        list: Una lista de strings, donde cada string es el nombre de una organización.
              La lista no contiene duplicados. Si no se encuentran organizaciones,
              devuelve una lista vacía.
    """
    client = language_v2.LanguageServiceClient.from_service_account_file(CREDENTIALS)
    organization_names = []  # Lista para almacenar los nombres de las organizaciones

    for i, review_text in enumerate(reviews):
        try:
            document = language_v2.Document(
                content=review_text, 
                type_=language_v2.Document.Type.PLAIN_TEXT,
                language_code="es"  # o "en", dependiendo del idioma de tus reseñas
            )
            encoding_type = language_v2.EncodingType.UTF8
            response = client.analyze_entities(
                request={"document": document, "encoding_type": encoding_type}
            )

            print(f"\n--- Organizaciones de la Reseña {i+1} ---")
            for entity in response.entities:
                entity_type = language_v2.Entity.Type(entity.type_).name
                if entity_type == "ORGANIZATION":
                    entity_name = entity.name
                    print(f"  Organización: {entity_name}")
                    if entity_name not in organization_names:
                        organization_names.append(entity_name)

        except Exception as e:
            print(f"Error al extraer organizaciones de la reseña {i+1}: {e}")
            # Registra el error para depuración, pero continúa con las otras reseñas
            continue  

    return organization_names

def classify_sentiment_results(main_business: Business, competitors: list[Business]) -> list[str]:
    """
    Clasifica el sentimiento del negocio principal y sus competidores,
    ordenándolos de mejor a peor basándose en una combinación ponderada
    de la puntuación de sentimiento y la magnitud."""
    all_businesses_data = []

    # Procesar el negocio principal
    if main_business.sentimiento_medio is not None and main_business.magnitud_sentimiento_media is not None:
        combined_score = main_business.sentimiento_medio * main_business.magnitud_sentimiento_media
        all_businesses_data.append({
            "nombre": main_business.nombre,
            "place_id": main_business.place_id,
            "puntuacion_promedio": main_business.sentimiento_medio,
            "magnitud_promedio": main_business.magnitud_sentimiento_media,
            "combined_score": combined_score
        })
    else:
        print(f"Advertencia: No hay datos de sentimiento válidos para el negocio principal: {main_business.nombre}")

    # Procesar los competidores
    for competitor in competitors:
        if competitor.sentimiento_medio is not None and competitor.magnitud_sentimiento_media is not None:
            combined_score = competitor.sentimiento_medio * competitor.magnitud_sentimiento_media
            all_businesses_data.append({
                "nombre": competitor.nombre,
                "place_id": competitor.place_id,
                "puntuacion_promedio": competitor.sentimiento_medio,
                "magnitud_promedio": competitor.magnitud_sentimiento_media,
                "combined_score": combined_score
            })
        else:
            print(f"Advertencia: No hay datos de sentimiento válidos para el competidor: {competitor.nombre}")

    if not all_businesses_data:
        print("No hay negocios con datos de sentimiento válidos para clasificar.")
        return []

    # Clasificar por la puntuación combinada (mayor es mejor)
    # Si hay empate en la puntuación combinada, se puede usar la magnitud o la puntuación
    # promedio como desempate secundario para una ordenación más estable.
    # Aquí, priorizamos combined_score, luego puntuacion_promedio y finalmente magnitud_promedio
    ordered_businesses_data = sorted(
        all_businesses_data,
        key=lambda item: (item["combined_score"], item["puntuacion_promedio"], item["magnitud_promedio"]),
        reverse=True
    )

    sentiment_order=[]

    # --- PARA VISUALIZACIÓN ---
    print("\n--- Clasificación del Sentimiento (por puntuación combinada) ---")
    for i, business in enumerate(ordered_businesses_data):
        print(f"{i+1}. {business['nombre']} (ID: {business['place_id']}):")
        print(f"   Puntuación Promedio = {business['puntuacion_promedio']:.4f}")
        print(f"   Magnitud Promedio   = {business['magnitud_promedio']:.4f}")
        print(f"   Puntuación Combinada = {business['combined_score']:.4f}")
        print("-" * 30)
        sentiment_order.append({business["nombre"]:i+1})

    # Determinar los "mejores" negocios (podría ser uno o varios si tienen la misma puntuación combinada)
    best_combined_score = ordered_businesses_data[0]["combined_score"]
    top_performers = [
        business["nombre"] for business in ordered_businesses_data if business["combined_score"] == best_combined_score
    ]

    print("\nNegocio(s) con la mejor puntuación combinada de sentimiento:", ", ".join(top_performers))
    # ---------------------------------------------------------------
    print(sentiment_order)
    return sentiment_order

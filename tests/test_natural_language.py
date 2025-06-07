import pytest
from unittest.mock import MagicMock, patch
from backend.business.models import Business, BusinessReview, BusinessAddress
from backend.processing.natural_language import (
    sentiment_analysis,
    analyze_reviews_sentiment,
    analyze_keyword_sentiment,
    extract_organizations_from_reviews,
    classify_sentiment_results # Nombre de función actualizado
)
from google.cloud import language_v1 # Para el cliente real
from google.cloud import language_v2 # Para el cliente real

# Mock para la variable de entorno de credenciales
@pytest.fixture(autouse=True)
def mock_credentials_env():
    with patch.dict('os.environ', {'GOOGLE_APPLICATION_CREDENTIALS': '/mock/path/to/credentials.json'}):
        yield

# --- Test analyze_reviews_sentiment ---
@patch('backend.processing.natural_language.language_v1.LanguageServiceClient.from_service_account_file')
def test_analyze_reviews_sentiment_exitoso(mock_client_factory):
    """
    Comprueba el análisis de sentimiento exitoso de múltiples reseñas, calculando promedios.
    """
    mock_client = MagicMock()
    mock_client_factory.return_value = mock_client

    # Mock de respuestas para el análisis de sentimiento de reseñas individuales
    mock_sentiment_pos = MagicMock()
    mock_sentiment_pos.document_sentiment.score = 0.8
    mock_sentiment_pos.document_sentiment.magnitude = 0.9

    mock_sentiment_neg = MagicMock()
    mock_sentiment_neg.document_sentiment.score = -0.5
    mock_sentiment_neg.document_sentiment.magnitude = 0.6

    mock_sentiment_neutral = MagicMock()
    mock_sentiment_neutral.document_sentiment.score = 0.1
    mock_sentiment_neutral.document_sentiment.magnitude = 0.1

    mock_client.analyze_sentiment.side_effect = [
        mock_sentiment_pos, mock_sentiment_neg, mock_sentiment_neutral
    ]

    reviews = ["¡Gran producto!", "Muy mala experiencia.", "Estuvo bien."]
    result = analyze_reviews_sentiment(reviews)

    assert result is not None
    # Puntuación promedio esperada: (0.8 + (-0.5) + 0.1) / 3 = 0.4 / 3 = 0.1333
    # Magnitud promedio esperada: (0.9 + 0.6 + 0.1) / 3 = 1.6 / 3 = 0.5333
    assert result["average_score"] == pytest.approx(0.1333, rel=1e-3)
    assert result["average_magnitude"] == pytest.approx(0.5333, rel=1e-3)
    assert mock_client.analyze_sentiment.call_count == 3
    print(f"✅ Test 'test_analyze_reviews_sentiment_exitoso' Passed.")

@patch('backend.processing.natural_language.language_v1.LanguageServiceClient.from_service_account_file')
def test_analyze_reviews_sentiment_sin_reseñas_validas(mock_client_factory):
    """
    Comprueba el escenario donde no se proporcionan reseñas válidas o el análisis falla para todas.
    """
    mock_client = MagicMock()
    mock_client_factory.return_value = mock_client
    mock_client.analyze_sentiment.side_effect = Exception("API Error") # Simula el fallo del análisis

    reviews = ["Reseña inválida 1", "Reseña inválida 2"]
    result = analyze_reviews_sentiment(reviews)

    assert result is None
    print(f"✅ Test 'test_analyze_reviews_sentiment_sin_reseñas_validas' Passed.")

@patch('backend.processing.natural_language.language_v2.LanguageServiceClient.from_service_account_file')
def test_extract_organizations_from_reviews_sin_organizaciones(mock_client_factory):
    """
    Comprueba el escenario donde no se encuentran organizaciones en las reseñas.
    """
    mock_client = MagicMock()
    mock_client_factory.return_value = mock_client

    mock_response = MagicMock()
    entity_person = MagicMock(name="Persona A", type_=language_v2.Entity.Type.PERSON)
    mock_response.entities = [entity_person]
    mock_client.analyze_entities.return_value = mock_response

    reviews = ["Esta reseña habla de Persona A."]
    organizations = extract_organizations_from_reviews(reviews)

    assert organizations == []
    print(f"✅ Test 'test_extract_organizations_from_reviews_sin_organizaciones' Passed.")

# --- Test sentiment_analysis (tipo integración) ---
@patch('backend.processing.natural_language.analyze_reviews_sentiment')
@patch('backend.processing.natural_language.analyze_keyword_sentiment')
@patch('backend.processing.natural_language.extract_organizations_from_reviews')
def test_sentiment_analysis_flujo_completo(mock_extract_orgs, mock_analyze_keywords, mock_analyze_sentiment_reviews):
    """
    Comprueba la función principal de orquestación sentiment_analysis.
    """
    main_business = Business(
        place_id="main_id",
        main_business=True,
        palabra_busqueda="categoría",
        nombre="Negocio Principal",
        reviews_traducidas=["reseña principal 1", "reseña principal 2"]
    )
    competitor1 = Business(
        place_id="comp1_id",
        main_business=False,
        palabra_busqueda="categoría",
        nombre="Competidor 1",
        reviews_traducidas=["reseña comp1 1"]
    )
    competitor2 = Business(
        place_id="comp2_id",
        main_business=False,
        palabra_busqueda="categoría",
        nombre="Competidor 2",
        reviews_traducidas=["reseña comp2 1", "reseña comp2 2"]
    )

    # Mock de valores de retorno para las sub-funciones
    mock_analyze_sentiment_reviews.side_effect = [
        {"average_score": 0.7, "average_magnitude": 0.8}, # Negocio Principal
        {"average_score": 0.2, "average_magnitude": 0.3}, # Competidor 1
        {"average_score": 0.9, "average_magnitude": 0.95} # Competidor 2 (mejor sentimiento)
    ]
    mock_analyze_keywords.side_effect = [
        (["positivo_principal"], ["negativo_principal"]),
        (["positivo_comp1"], ["negativo_comp1"]),
        (["positivo_comp2"], ["negativo_comp2"])
    ]

    mock_analyze_keywords.side_effect = [
    ([("positivo_principal", 0.8)], [("negativo_principal", -0.7)])]# Formato correcto: lista de tuplas (palabra, puntuación]
    mock_extract_orgs.return_value = ["OrgPrincipal", "OtraOrg"] # Solo para el negocio principal

    businesses = [main_business, competitor1, competitor2]
    sentiment_analysis(main_business, [competitor1, competitor2])

    # main_business
    assert main_business.sentimiento_medio == 0.7
    assert main_business.magnitud_sentimiento_media == 0.8
    assert "positivo_principal" in main_business.palabras_connotacion_positiva
    assert "negativo_principal" in main_business.palabras_connotacion_negativa
    assert "OrgPrincipal" in main_business.palabras_clave_en_resenas
    assert "OtraOrg" in main_business.palabras_clave_en_resenas

    # Competitor1
    assert competitor1.sentimiento_medio == 0.2
    assert competitor1.magnitud_sentimiento_media == 0.3

    # Competitor2
    assert competitor2.sentimiento_medio == 0.9
    assert competitor2.magnitud_sentimiento_media == 0.95

    # Comprueba el orden de sentimiento
    assert main_business.orden_por_sentimiento is not None
    assert competitor1.orden_por_sentimiento is not None
    assert competitor2.orden_por_sentimiento is not None
    
    # El orden debería ser: Competidor 2 (1), Negocio Principal (2), Competidor 1 (3)
    #porque el Competidor 2 tiene la puntuación combinada más alta (0.9 * 0.95 = 0.855)
    
    # Orden 
    order_dict = {}
    for b in businesses:
        if b.orden_por_sentimiento is not None:
            order_dict[b.nombre] = b.orden_por_sentimiento

    assert order_dict["Competidor 2"] == 1
    assert order_dict["Negocio Principal"] == 2
    assert order_dict["Competidor 1"] == 3
    print(f"✅ Test 'test_sentiment_analysis_flujo_completo' Passed.")

# --- Test classify_sentiment_results ---
def test_classify_sentiment_results_ordenacion():
    """
    Comprueba la correcta ordenación de los negocios basada en la puntuación de sentimiento combinada.
    """
    business_a = Business(nombre="Negocio A", place_id="A", main_business=True, palabra_busqueda="x")
    business_a.set_sentiment_analysis({"average_score": 0.8, "average_magnitude": 0.7}, [], [], []) # Combinado: 0.56

    business_b = Business(nombre="Negocio B", place_id="B", main_business=False, palabra_busqueda="x")
    business_b.set_sentiment_analysis({"average_score": 0.5, "average_magnitude": 0.9}, [], [], []) # Combinado: 0.45

    business_c = Business(nombre="Negocio C", place_id="C", main_business=False, palabra_busqueda="x")
    business_c.set_sentiment_analysis({"average_score": 0.8, "average_magnitude": 0.5}, [], [], []) # Combinado: 0.40 (magnitud menor que A)

    # Como sentiment_analysis en la aplicación llama a classify_sentiment_results internamente,
    # para probarla de forma aislada, le pasamos los objetos de negocio pre-procesados.
    
    result_order = classify_sentiment_results(business_a, [business_b, business_c])

    # Convierte la lista de diccionarios a un solo diccionario para que sea mas facil
    ordered_map = {list(d.keys())[0]: list(d.values())[0] for d in result_order}

    assert ordered_map["Negocio A"] == 1
    assert ordered_map["Negocio B"] == 2
    assert ordered_map["Negocio C"] == 3
    print(f"✅ Test 'test_classify_sentiment_results_ordenacion' Passed.")

def test_classify_sentiment_results_sin_datos_sentimiento():
    """
    Comprueba el escenario donde los negocios no tienen datos de sentimiento.
    """
    business_d = Business(nombre="Negocio D", place_id="D", main_business=True, palabra_busqueda="x") 
    business_e = Business(nombre="Negocio E", place_id="E", main_business=False, palabra_busqueda="x") 

    result = classify_sentiment_results(business_d, [business_e])
    assert result == [] 
    print(f"✅ Test 'test_classify_sentiment_results_sin_datos_sentimiento' Passed.")
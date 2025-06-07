import pytest
from unittest.mock import MagicMock, patch
from backend.business.models import Business, BusinessReview, SentimentResult
from backend.processing.natural_language import (
    analyze_reviews_sentiment,
    analyze_keyword_sentiment,
    sentiment_analysis,
    rank_businesses_by_sentiment
)

# Mock para la variable de entorno de credenciales
@pytest.fixture(autouse=True)
def mock_credentials_env():
    with patch.dict('os.environ', {'GOOGLE_APPLICATION_CREDENTIALS': '/mock/path/to/credentials.json'}):
        yield

@patch('google.cloud.language_v1.LanguageServiceClient.from_service_account_file')
def test_analyze_reviews_sentiment(mock_client_factory):
    mock_client = MagicMock()
    mock_client_factory.return_value = mock_client

    # Simular respuesta de la API de Natural Language
    mock_document = MagicMock()
    mock_analyze_sentiment_response = MagicMock()
    mock_analyze_sentiment_response.document_sentiment.score = 0.8
    mock_analyze_sentiment_response.document_sentiment.magnitude = 0.9

    mock_client.analyze_sentiment.return_value = mock_analyze_sentiment_response

    reviews = ["Esta es una reseña muy positiva.", "Me encantó el servicio."]
    result = analyze_reviews_sentiment(reviews)

    assert isinstance(result, SentimentResult)
    assert result.score == pytest.approx(0.8)
    assert result.magnitude == pytest.approx(0.9)
    assert mock_client.analyze_sentiment.call_count == 2 # Dos llamadas, una por cada reseña

@patch('google.cloud.language_v1.LanguageServiceClient.from_service_account_file')
def test_analyze_keyword_sentiment(mock_client_factory):
    mock_client = MagicMock()
    mock_client_factory.return_value = mock_client

    # Simular respuesta de la API de Natural Language para análisis de entidades
    mock_analyze_entity_sentiment_response_positive = MagicMock()
    mock_entity_positive = MagicMock()
    mock_entity_positive.name = "excelente"
    mock_entity_positive.sentiment.score = 0.9
    mock_entity_positive.sentiment.magnitude = 1.0
    mock_analyze_entity_sentiment_response_positive.entities = [mock_entity_positive]

    mock_analyze_entity_sentiment_response_negative = MagicMock()
    mock_entity_negative = MagicMock()
    mock_entity_negative.name = "malo"
    mock_entity_negative.sentiment.score = -0.8
    mock_entity_negative.sentiment.magnitude = 0.7
    mock_analyze_entity_sentiment_response_negative.entities = [mock_entity_negative]

    # Configurar el side_effect para que devuelva diferentes respuestas según la llamada
    mock_client.analyze_entity_sentiment.side_effect = [
        mock_analyze_entity_sentiment_response_positive,
        mock_analyze_entity_sentiment_response_negative
    ]

    reviews = ["El servicio fue excelente.", "La espera fue mala."]
    top_positive, top_negative = analyze_keyword_sentiment(reviews)

    assert "excelente" in top_positive
    assert "malo" in top_negative
    assert "malo" not in top_positive
    assert "excelente" not in top_negative

@patch('backend.processing.natural_language.analyze_reviews_sentiment')
@patch('backend.processing.natural_language.analyze_keyword_sentiment')
@patch('backend.processing.natural_language.extract_organizations_from_reviews')
def test_sentiment_analysis(mock_extract_organizations, mock_analyze_keywords, mock_analyze_reviews):
    main_business = Business(nombre="Main Business", reviews=[
        BusinessReview(texto="Good review")
    ])
    competitor1 = Business(nombre="Comp 1", reviews=[
        BusinessReview(texto="Bad review")
    ])
    competitor2 = Business(nombre="Comp 2", reviews=[
        BusinessReview(texto="Neutral review")
    ])

    # Mockear las respuestas de las funciones auxiliares
    mock_analyze_reviews.side_effect = [
        SentimentResult(score=0.5, magnitude=0.6), # Main business
        SentimentResult(score=-0.2, magnitude=0.3), # Competitor 1
        SentimentResult(score=0.1, magnitude=0.1) # Competitor 2
    ]
    mock_analyze_keywords.side_effect = [
        (["good"], ["bad"]), # Main business
        (["ok"], ["terrible"]), # Competitor 1
        (["fine"], ["ugly"]) # Competitor 2
    ]
    mock_extract_organizations.return_value = ["Org A"]

    sentiment_analysis(main_business, [competitor1, competitor2])

    # Verificar que se llamaron a las funciones con los datos correctos
    mock_analyze_reviews.assert_any_call([main_business.reviews[0].texto])
    mock_analyze_reviews.assert_any_call([competitor1.reviews[0].texto])
    mock_analyze_reviews.assert_any_call([competitor2.reviews[0].texto])

    assert main_business.sentimiento_medio == pytest.approx(0.5)
    assert main_business.magnitud_sentimiento_media == pytest.approx(0.6)
    assert "good" in main_business.palabras_connotacion_positiva
    assert "bad" in main_business.palabras_connotacion_negativa

    assert competitor1.sentimiento_medio == pytest.approx(-0.2)
    assert competitor1.magnitud_sentimiento_media == pytest.approx(0.3)
    assert "ok" in competitor1.palabras_connotacion_positiva
    assert "terrible" in competitor1.palabras_connotacion_negativa

    assert competitor2.sentimiento_medio == pytest.approx(0.1)
    assert competitor2.magnitud_sentimiento_media == pytest.approx(0.1)
    assert "fine" in competitor2.palabras_connotacion_positiva
    assert "ugly" in competitor2.palabras_connotacion_negativa

@patch('backend.processing.natural_language.analyze_reviews_sentiment')
def test_rank_businesses_by_sentiment(mock_analyze_reviews):
    business1 = Business(nombre="Business A", reviews=[BusinessReview(texto="Review A")])
    business2 = Business(nombre="Business B", reviews=[BusinessReview(texto="Review B")])
    business3 = Business(nombre="Business C", reviews=[BusinessReview(texto="Review C")])

    # Mockear el análisis de sentimiento para cada negocio
    mock_analyze_reviews.side_effect = [
        SentimentResult(score=0.8, magnitude=0.7), # Business A
        SentimentResult(score=0.5, magnitude=0.9), # Business B
        SentimentResult(score=0.8, magnitude=0.5)  # Business C (mismo score que A, pero menor magnitud)
    ]

    sentiment_analysis(business1, [business2, business3])
    ranked_order = rank_businesses_by_sentiment([business1, business2, business3])

    # Esperamos que Business A sea el 1ro (score 0.8, mag 0.7)
    # Business C sea el 2do (score 0.8, mag 0.5)
    # Business B sea el 3ro (score 0.5, mag 0.9)
    assert ranked_order[0]["Business A"] == 1
    assert ranked_order[1]["Business C"] == 2
    assert ranked_order[2]["Business B"] == 3
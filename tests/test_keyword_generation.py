import pytest
from unittest.mock import MagicMock, patch
from backend.ingestion.keywords.keyword_generation import get_keyword_ideas
import os

# Mock de las variables de entorno (como DEVELOPER_TOKEN, LOGIN_CUSTOMER_ID) si se acceden.
@pytest.fixture(autouse=True)
def mock_ads_env_vars():
    with patch.dict(os.environ, {"DEVELOPER_TOKEN": "mock_dev_token", "LOGIN_CUSTOMER_ID": "mock_customer_id"}):
        yield

@patch('google.ads.googleads.client.GoogleAdsClient')
def test_get_keyword_ideas_filtrado(mock_google_ads_client):
    """
    Comprueba que las ideas de palabras clave se filtran correctamente según el índice de competencia,
    las búsquedas mensuales, la palabra clave 'gratis' y los grupos de conceptos.
    """
    # Configura el mock del cliente de Google Ads
    mock_client_instance = MagicMock()
    mock_google_ads_client.return_value = mock_client_instance

    mock_service = MagicMock()
    mock_client_instance.get_service.return_value = mock_service

    mock_request = MagicMock()
    mock_client_instance.get_type.return_value = mock_request

    # Configura los enums (importante para un mocking preciso)
    mock_client_instance.enums.KeywordPlanNetworkEnum.GoogleSEARCH_AND_PARTNERS = 1
    mock_client_instance.enums.KeywordPlanKeywordAnnotationEnum.KEYWORD_CONCEPT = 1

    # Define ideas de palabras clave mock con varias propiedades
    mock_idea_included_1 = MagicMock()
    mock_idea_included_1.text = "electricista a domicilio"
    mock_idea_included_1.keyword_idea_metrics.competition_index = 50 # Incluido
    mock_idea_included_1.keyword_idea_metrics.avg_monthly_searches = 100
    mock_idea_included_1.keyword_annotations.concepts = []

    mock_idea_excluded_competition = MagicMock()
    mock_idea_excluded_competition.text = "electricista barato"
    mock_idea_excluded_competition.keyword_idea_metrics.competition_index = 70 # Excluido (demasiado alto)
    mock_idea_excluded_competition.keyword_idea_metrics.avg_monthly_searches = 50
    mock_idea_excluded_competition.keyword_annotations.concepts = []

    mock_idea_excluded_low_searches = MagicMock()
    mock_idea_excluded_low_searches.text = "electricista urgente"
    mock_idea_excluded_low_searches.keyword_idea_metrics.competition_index = 40
    mock_idea_excluded_low_searches.keyword_idea_metrics.avg_monthly_searches = 10 # Excluido (demasiado bajo)
    mock_idea_excluded_low_searches.keyword_annotations.concepts = []

    mock_idea_excluded_brand_concept = MagicMock()
    mock_idea_excluded_brand_concept.text = "electricista Bosch"
    mock_idea_excluded_brand_concept.keyword_idea_metrics.competition_index = 30
    mock_idea_excluded_brand_concept.keyword_idea_metrics.avg_monthly_searches = 200
    mock_concept_brand = MagicMock()
    mock_concept_brand.name = "Bosch"
    mock_concept_brand.concept_group.name = "Marcas"
    mock_idea_excluded_brand_concept.keyword_annotations.concepts = [mock_concept_brand]

    mock_idea_excluded_wrong_city = MagicMock()
    mock_idea_excluded_wrong_city.text = "electricista en sevilla"
    mock_idea_excluded_wrong_city.keyword_idea_metrics.competition_index = 30
    mock_idea_excluded_wrong_city.keyword_idea_metrics.avg_monthly_searches = 200
    mock_concept_wrong_city = MagicMock()
    mock_concept_wrong_city.name = "Sevilla"
    mock_concept_wrong_city.concept_group.name = "Ciudad"
    mock_idea_excluded_wrong_city.keyword_annotations.concepts = [mock_concept_wrong_city]

    mock_idea_excluded_gratis = MagicMock()
    mock_idea_excluded_gratis.text = "electricista gratis" # Excluido (contiene 'gratis')
    mock_idea_excluded_gratis.keyword_idea_metrics.competition_index = 10
    mock_idea_excluded_gratis.keyword_idea_metrics.avg_monthly_searches = 50
    mock_idea_excluded_gratis.keyword_annotations.concepts = []

    mock_idea_included_city = MagicMock()
    mock_idea_included_city.text = "electricista en córdoba"
    mock_idea_included_city.keyword_idea_metrics.competition_index = 25 # Incluido
    mock_idea_included_city.keyword_idea_metrics.avg_monthly_searches = 150
    mock_concept_correct_city = MagicMock()
    mock_concept_correct_city.name = "Córdoba"
    mock_concept_correct_city.concept_group.name = "Ciudad"
    mock_idea_included_city.keyword_annotations.concepts = [mock_concept_correct_city]

    mock_service.generate_keyword_ideas.return_value = [
        mock_idea_included_1, mock_idea_excluded_competition, mock_idea_excluded_low_searches,
        mock_idea_excluded_brand_concept, mock_idea_excluded_wrong_city, mock_idea_excluded_gratis,
        mock_idea_included_city
    ]

    # Llama a la función con datos de prueba
    category = "electricista"
    city = "córdoba"
    result_ideas = get_keyword_ideas(mock_client_instance, category, city)

    # Asertos
    assert len(result_ideas) == 2
    
    # Comprueba la presencia de ideas incluidas
    expected_idea_1 = {"keyword": "electricista a domicilio", "indice_competicion": 50, "busquedas_mensuales": 100, "concepts": []}
    expected_idea_city = {"keyword": "electricista en córdoba", "indice_competicion": 25, "busquedas_mensuales": 150, "concepts": [mock_concept_correct_city]}
    
    assert expected_idea_1 in result_ideas
    assert expected_idea_city in result_ideas
    
    # Asegura que las ideas excluidas no están presentes
    assert not any("electricista barato" in d["keyword"] for d in result_ideas)
    assert not any("electricista urgente" in d["keyword"] for d in result_ideas)
    assert not any("electricista Bosch" in d["keyword"] for d in result_ideas)
    assert not any("electricista en sevilla" in d["keyword"] for d in result_ideas)
    assert not any("electricista gratis" in d["keyword"] for d in result_ideas)
    
    print(f"✅ Test 'test_get_keyword_ideas_filtrado' Passed.")
import pytest
from unittest.mock import MagicMock, patch
from backend.ingestion.keywords.keyword_generation import get_keyword_ideas

@patch('google.ads.googleads.client.GoogleAdsClient')
def test_get_keyword_ideas(mock_google_ads_client):
    # Configurar el mock del cliente de Google Ads
    mock_client_instance = MagicMock()
    mock_google_ads_client.return_value = mock_client_instance

    mock_service = MagicMock()
    mock_client_instance.get_service.return_value = mock_service

    mock_request = MagicMock()
    mock_client_instance.get_type.return_value = mock_request

    # Configurar los enums
    mock_client_instance.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS = 1
    mock_client_instance.enums.KeywordPlanKeywordAnnotationEnum.KEYWORD_CONCEPT = 1

    # Crear ideas de palabras clave simuladas
    mock_idea1 = MagicMock() # Debería ser incluida
    mock_idea1.text = "electricista a domicilio"
    mock_idea1.keyword_idea_metrics.competition_index = 50
    mock_idea1.keyword_idea_metrics.avg_monthly_searches = 100
    mock_idea1.keyword_annotations.concepts = [] # Sin conceptos que excluyan

    mock_idea2 = MagicMock() # Debería ser excluida por competencia
    mock_idea2.text = "electricista barato"
    mock_idea2.keyword_idea_metrics.competition_index = 70
    mock_idea2.keyword_idea_metrics.avg_monthly_searches = 50
    mock_idea2.keyword_annotations.concepts = []

    mock_idea3 = MagicMock() # Debería ser excluida por bajas búsquedas
    mock_idea3.text = "electricista urgente"
    mock_idea3.keyword_idea_metrics.competition_index = 40
    mock_idea3.keyword_idea_metrics.avg_monthly_searches = 10
    mock_idea3.keyword_annotations.concepts = []

    mock_idea4 = MagicMock() # Debería ser excluida por concepto (Marca)
    mock_idea4.text = "electricista Bosch"
    mock_idea4.keyword_idea_metrics.competition_index = 30
    mock_idea4.keyword_idea_metrics.avg_monthly_searches = 200
    mock_concept4 = MagicMock()
    mock_concept4.name = "Bosch"
    mock_concept4.concept_group.name = "Marcas" # Simula un concepto de marca
    mock_idea4.keyword_annotations.concepts = [mock_concept4]

    mock_idea5 = MagicMock() # Debería ser excluida por concepto (Ciudad incorrecta)
    mock_idea5.text = "electricista en sevilla"
    mock_idea5.keyword_idea_metrics.competition_index = 30
    mock_idea5.keyword_idea_metrics.avg_monthly_searches = 200
    mock_concept5 = MagicMock()
    mock_concept5.name = "Sevilla"
    mock_concept5.concept_group.name = "Ciudad"
    mock_idea5.keyword_annotations.concepts = [mock_concept5]

    mock_idea6 = MagicMock() # Debería ser excluida por "gratis"
    mock_idea6.text = "electricista gratis"
    mock_idea6.keyword_idea_metrics.competition_index = 10
    mock_idea6.keyword_idea_metrics.avg_monthly_searches = 50
    mock_idea6.keyword_annotations.concepts = []

    mock_idea7 = MagicMock() # Debería ser incluida (ciudad correcta)
    mock_idea7.text = "electricista en córdoba"
    mock_idea7.keyword_idea_metrics.competition_index = 25
    mock_idea7.keyword_idea_metrics.avg_monthly_searches = 150
    mock_concept7 = MagicMock()
    mock_concept7.name = "Córdoba"
    mock_concept7.concept_group.name = "Ciudad"
    mock_idea7.keyword_annotations.concepts = [mock_concept7]

    mock_service.generate_keyword_ideas.return_value = [
        mock_idea1, mock_idea2, mock_idea3, mock_idea4, mock_idea5, mock_idea6, mock_idea7
    ]

    # Llamar a la función
    categoria = "electricista"
    ciudad = "córdoba"
    result = get_keyword_ideas(mock_client_instance, categoria, ciudad)

    # Verificar los resultados
    assert len(result) == 2
    assert {"keyword": "electricista a domicilio", "indice_competicion": 50, "busquedas_mensuales": 100, "concepts": []} in result
    assert {"keyword": "electricista en córdoba", "indice_competicion": 25, "busquedas_mensuales": 150, "concepts": [mock_concept7]} in result

    # Verificar que las excluidas no están
    assert {"keyword": "electricista barato", "indice_competicion": 70, "busquedas_mensuales": 50, "concepts": []} not in result
    assert {"keyword": "electricista urgente", "indice_competicion": 40, "busquedas_mensuales": 10, "concepts": []} not in result
    assert {"keyword": "electricista Bosch", "indice_competicion": 30, "busquedas_mensuales": 200, "concepts": [mock_concept4]} not in result
    assert {"keyword": "electricista en sevilla", "indice_competicion": 30, "busquedas_mensuales": 200, "concepts": [mock_concept5]} not in result
    assert {"keyword": "electricista gratis", "indice_competicion": 10, "busquedas_mensuales": 50, "concepts": []} not in result
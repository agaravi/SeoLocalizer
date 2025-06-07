import pytest
import requests
from unittest.mock import patch, MagicMock
from backend.ingestion.scraping.Zyte_Firmania_scraper import buscar_negocio_firmania
import os

# Mockear la clave API para evitar errores si no está configurada
@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict(os.environ, {"ZYTE_APIKEY": "mock_zyte_key"}):
        yield

@patch('requests.post')
def test_buscar_negocio_firmania_encontrado(mock_post):
    # Simular una respuesta exitosa de Zyte API con un negocio encontrado
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Ejemplo de contenido HTML simplificado para un negocio encontrado
    mock_response.json.return_value = {
        "httpResponseBody": "PGh0bWw+PGJvZHk+PGEgaHJlZj0iL2VtY2VsbWVudG8tdXJsdCI+RXNwZWNpYWxpc3RhcyBlbiBFbGVjdHJpY2lkYWQ8L2E+PC9ib2R5PjwvaHRtbD4=" # Base64 de <html><body><a href="/emcelmento-url">Especialistas en Electricidad</a></body></html>
    }
    mock_post.return_value = mock_response

    # Datos de entrada
    nombre = "Especialistas en Electricidad"
    ciudad = "Córdoba"
    provincia = "Córdoba"
    direccion = "Calle Falsa 123"

    # La normalización de la dirección en el scraper compararía con un nombre similar
    with patch('backend.ingestion.scraping.normalizations.similarity', return_value=0.95):
        with patch('backend.ingestion.scraping.normalizations.normalize_address', side_effect=lambda x: x.lower()):
            result = buscar_negocio_firmania(nombre, ciudad, provincia, direccion)

    assert result["Encontrado"] == "Si"
    assert result["Nombre"] == "Especialistas en Electricidad"
    assert result["Localidad"] == "Córdoba" # Debería tomarlo de la entrada si no lo saca del HTML
    assert result["Similaridad_direccion"] == 0.95
    assert result["Error"] is None

@patch('requests.post')
def test_buscar_negocio_firmania_no_encontrado(mock_post):
    # Simular una respuesta de Zyte API sin resultados de negocio
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "httpResponseBody": "PGh0bWw+PGJvZHk+PGRpdiBjbGFzcz0ibm8tcmVzdWx0cyI+Tm8gc2UgZW5jb250cmFyb24gcmVzdWx0YWRvczwvZGl2PjwvYm9keT48L2h0bWw+" # Base64 de HTML sin el link del negocio
    }
    mock_post.return_value = mock_response

    nombre = "Negocio Inexistente"
    ciudad = "Ciudad Ficticia"
    provincia = "Provincia Ficticia"
    direccion = "Calle Sin Fin"

    result = buscar_negocio_firmania(nombre, ciudad, provincia, direccion)
    assert result["Encontrado"] == "No"
    assert result["Nombre"] is None # O el nombre que se espera si lo devuelve el scraper incluso si no lo encuentra
    assert result["Error"] is None

@patch('requests.post')
def test_buscar_negocio_firmania_error_api(mock_post):
    # Simular un error HTTP de Zyte API
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    nombre = "Cualquier Negocio"
    ciudad = "Cualquier Ciudad"
    provincia = "Cualquier Provincia"
    direccion = "Cualquier Direccion"

    result = buscar_negocio_firmania(nombre, ciudad, provincia, direccion)
    assert result["Encontrado"] == "No"
    assert "Error en la solicitud" in result["Error"]
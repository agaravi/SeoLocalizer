import pytest
import requests
from unittest.mock import patch, MagicMock
from backend.ingestion.scraping.Zyte_Firmania_scraper import buscar_negocio_firmania
import os
import base64

# Mock de la clave API para evitar errores si no está configurada, para todos los tests de este módulo.
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mocks la variable de entorno ZYTE_APIKEY para todos los tests."""
    with patch.dict(os.environ, {"ZYTE_APIKEY": "mock_zyte_key"}):
        yield

@patch('requests.post')
def test_buscar_negocio_firmania_error_api(mock_post):
    """
    Caso de test: La API de Zyte devuelve un error HTTP.
    Verifica que la función maneja los errores de la API de forma correcta.
    """
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response

    nombre = "Cualquier Negocio"
    ciudad = "Cualquier Ciudad"
    provincia = "Cualquier Provincia"
    direccion = "Cualquier Dirección"

    result = buscar_negocio_firmania(nombre, ciudad, provincia, direccion)
    assert result["Encontrado"] == "No"
    assert "Ha habido un problema con la API" in result["Error"]
    print(f"✅ Test 'test_buscar_negocio_firmania_error_api' Passed for '{nombre}'")

@patch('requests.post')
def test_buscar_negocio_firmania_no_bloque_resultados(mock_post):
    """
    Caso de test: La API de Zyte devuelve HTML, pero no se encuentra el bloque de resultados esperado.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    html_content = "<html><body><div>No hay elemento de resultados de búsqueda.</div></body></html>"
    mock_response.json.return_value = {
        "httpResponseBody": base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    }
    mock_post.return_value = mock_response

    nombre = "Negocio"
    ciudad = "Ciudad"
    provincia = "Provincia"
    direccion = "Dirección"

    result = buscar_negocio_firmania(nombre, ciudad, provincia, direccion)
    assert result["Encontrado"] == "No"
    assert result["Nombre"] is None
    assert result["Error"] is None # No hay error de API, pero el scraper no pudo encontrar la estructura HTML esperada.
    print(f"✅ Test 'test_buscar_negocio_firmania_no_bloque_resultados' Passed.")

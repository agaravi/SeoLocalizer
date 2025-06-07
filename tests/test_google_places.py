import pytest
from unittest.mock import patch, MagicMock
from backend.ingestion.google_places import get_google_places_data, get_details_main_place, get_details_place
import os

# Mock de la clave API para todos los tests de este módulo.
@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mocks la variable de entorno GOOGLE_PLACES_API_KEY para todos los tests."""
    with patch.dict(os.environ, {"GOOGLE_PLACES_API_KEY": "mock_google_places_key"}):
        yield

@patch('requests.post')
def test_get_google_places_data_exitoso_un_resultado(mock_post):
    """
    Comprueba la recuperación exitosa de un único ID de lugar para el negocio principal.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"places": [{"id": "place_id_1", "displayName": {"text": "Negocio Uno"}}]}
    mock_post.return_value = mock_response

    place_id = get_google_places_data("Negocio Uno", "Ciudad A", 1)

    mock_post.assert_called_once() # Asegura que fue llamado
    assert place_id == "place_id_1"
    print(f"✅ Test 'test_get_google_places_data_exitoso_un_resultado' Passed.")

@patch('requests.post')
def test_get_google_places_data_exitoso_multiples_resultados(mock_post):
    """
    Comprueba la recuperación exitosa de múltiples ID de lugar para los competidores.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"places": [
        {"id": "comp_id_1", "displayName": {"text": "Competidor A"}},
        {"id": "comp_id_2", "displayName": {"text": "Competidor B"}},
        {"id": "comp_id_3", "displayName": {"text": "Competidor C"}}
    ]}
    mock_post.return_value = mock_response

    place_ids = get_google_places_data("Categoría X", "Ciudad Y", 3)

    mock_post.assert_called_once()
    assert len(place_ids) == 3
    assert "comp_id_1" in place_ids
    assert "comp_id_2" in place_ids
    assert "comp_id_3" in place_ids
    print(f"✅ Test 'test_get_google_places_data_exitoso_multiples_resultados' Passed.")


@patch('requests.post')
def test_get_google_places_data_sin_resultados(mock_post):
    """
    Comprueba el escenario donde no se encuentran lugares para la consulta dada.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"places": []} # Lista de lugares vacía
    mock_post.return_value = mock_response

    place_id = get_google_places_data("Negocio Inexistente", "Ciudad Inexistente", 1)
    assert place_id == [] # Debería devolver una lista vacía si no hay lugares
    print(f"✅ Test 'test_get_google_places_data_sin_resultados' Passed.")

@patch('requests.post')
def test_get_google_places_data_error_api(mock_post):
    """
    Comprueba el manejo de errores cuando la API de Google Places devuelve un error HTTP.
    """
    mock_response = MagicMock()
    mock_response.status_code = 403 # Prohibido
    mock_response.text = "Clave API inválida"
    mock_post.return_value = mock_response

    place_id = get_google_places_data("Negocio", "Ciudad", 1)
    assert place_id == [] # Debería devolver una lista vacía en caso de error
    print(f"✅ Test 'test_get_google_places_data_error_api' Passed.")

@patch('requests.get')
def test_get_details_main_place_exitoso(mock_get):
    """
    Comprueba la recuperación exitosa de información detallada para el negocio principal.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "main_place_id",
        "displayName": {"text": "Nombre de Negocio Principal"},
        "formattedAddress": "Calle Principal 123, Cualquier Ciudad",
        "userRatingCount": 150,
        "rating": 4.5,
        "reviews": [{"originalText": {"text": "¡Gran lugar!"}}]
        # ... otros campos esperados por set_from_google_places
    }
    mock_get.return_value = mock_response

    details = get_details_main_place("main_place_id")

    mock_get.assert_called_once()
    assert details["id"] == "main_place_id"
    assert details["displayName"]["text"] == "Nombre de Negocio Principal"
    assert details["rating"] == 4.5
    assert len(details["reviews"]) == 1
    print(f"✅ Test 'test_get_details_main_place_exitoso' Passed.")

@patch('requests.get')
def test_get_details_place_exitoso(mock_get):
    """
    Comprueba la recuperación exitosa de información detallada para un competidor.
    Esto utiliza una máscara de campo ligeramente diferente, por lo que es bueno probarlo por separado.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "comp_place_id",
        "displayName": {"text": "Negocio Competidor"},
        "userRatingCount": 50,
        "rating": 3.8,
        "reviews": [{"originalText": {"text": "Servicio aceptable."}}]
        # ... otros campos esperados por get_details_place (subconjunto)
    }
    mock_get.return_value = mock_response

    details = get_details_place("comp_place_id")

    mock_get.assert_called_once()
    assert details["id"] == "comp_place_id"
    assert details["displayName"]["text"] == "Negocio Competidor"
    assert details["rating"] == 3.8
    assert len(details["reviews"]) == 1
    print(f"✅ Test 'test_get_details_place_exitoso' Passed.")
import unittest
from unittest.mock import patch, Mock
from backend.ingestion.google_places import *
import requests
import json
# Suponiendo que la función obtener_datos_negocio está en un módulo llamado 'mi_modulo'

class TestObtenerDatosNegocio(unittest.TestCase):

    @patch('mi_modulo.requests.post') # Patchamos requests.post en el módulo donde se usa
    def test_obtener_datos_negocio_exitoso(self, mock_post):
        # Configurar el mock para que devuelva una respuesta controlada
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"places": [{"id": "mock_place_id", "name": "Mock Business"}]}
        mock_response.raise_for_status.return_value = None # Simular que no hay error HTTP

        mock_post.return_value = mock_response # Cuando se llame a requests.post, devolverá mock_response

        # Ejecutar la función que queremos probar
        datos = get_google_places_data("Mi Negocio", "Mi Ciudad")

        # Verificar que requests.post fue llamado con los argumentos esperados
        mock_post.assert_called_once_with(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": "tu_api_key_de_test", # La key real aquí no importa porque la llamada está mockeada
                "X-Goog-FieldMask": "places.id"
            },
            json={"textQuery": "Mi Negocio Mi Ciudad"}
        )
        # Verificar el resultado de la función
        self.assertEqual(datos, {"places": [{"id": "mock_place_id", "name": "Mock Business"}]})

    @patch('mi_modulo.requests.post')
    def test_obtener_datos_negocio_error(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"error": "Not Found"}
        # Simular que raise_for_status sí lanza una excepción
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")

        mock_post.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError):
           get_google_places_data("Negocio Inexistente", "Ciudad X")

# Para ejecutar los tests:
# if __name__ == '__main__':
#     unittest.main()
from google.ads.googleads.client import GoogleAdsClient
import os

# Ruta al archivo JSON de la cuenta de servicio de Google Cloud. El archivo 
# contiene las credenciales necesarias para autenticarse con los servicios de Google.
SERVICE_CREDENTIALS = "/etc/secrets/tfg-google-service-account-key.json"

# Token de desarrollador de Google Ads. Se obtiene de las variables de entorno.
DEVELOPER_TOKEN = os.environ.get("DEVELOPER_TOKEN")

# ID de cliente de inicio de sesión de Google Ads (cuenta bajo la cual se realizan
# las operaciones de la API). Se obtiene de las variables de entorno.
LOGIN_CUSTOMER_ID = os.environ.get("LOGIN_CUSTOMER_ID")


def get_ads_client():
    """Crea un cliente de la API de Google Ads usando las credenciales.
    Devuelve Una instancia configurada del cliente de la API de Google Ads"""
    return GoogleAdsClient.load_from_dict({
            "developer_token": DEVELOPER_TOKEN, 
            "json_key_file_path": SERVICE_CREDENTIALS,
            "login_customer_id": LOGIN_CUSTOMER_ID,
            "use_proto_plus":True
    })

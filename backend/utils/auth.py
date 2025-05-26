from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from google.ads.googleads.client import GoogleAdsClient
import os
import json
import yaml
from flask import session

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Obtiene el directorio base (backend)
#CLIENT_CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'oauth2_credentials.json')
#CLIENT_CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'auth_credentials_desktop2.json')

#CREDENTIALS_FILE = os.path.join(BASE_DIR, 'config', 'google_ads_credentials.json')

CLIENT_CONFIG_FILE = "/etc/secrets/oauth2_credentials.json"
CREDENTIALS_FILE = "/etc/secrets/google_ads_credentials.json"
SERVICE_CREDENTIALS = "/etc/secrets/tfg-google-service-account-key.json"
DEVELOPER_TOKEN=os.environ.get("DEVELOPER_TOKEN")

#GOOGLE_ADS_CONFIG_FILE = "/etc/secrets/google_ads_config.yaml"

# Scopes (permisos)
SCOPES = [
    'https://www.googleapis.com/auth/adwords',
    'https://www.googleapis.com/auth/datastudio'
    # Agrega aquí los scopes necesarios para Looker Studio API
]



def generate_auth_url(redirect_uri: str) -> str:
    """
    Genera la URL de autorización para que el usuario inicie sesión y dé su consentimiento.
    Args:
        redirect_uri (str): La URI de redirección registrada para tu cliente OAuth.
    Returns:
        str: La URL a la que el usuario debe ser redirigido para autenticarse.
    """
    flow = Flow.from_client_secrets_file(
        CLIENT_CONFIG_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri 
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline', # Necesario para obtener un refresh token
        prompt='consent'       # Forzar la pantalla de consentimiento
    )
    session['oauth_state'] = state # Almacena el 'state' en la sesión de Flask para verificación
    return authorization_url

def generate_auth_url_cli():
    """Genera la URL de autorización para la línea de comandos."""
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_CONFIG_FILE, SCOPES,redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    return auth_url

 
    
def exchange_code_for_token(authorization_response_url: str, redirect_uri: str) -> bool:
    """
    Intercambia el código de autorización por un token de acceso y un refresh token.
    Guarda las credenciales en la sesión de Flask y en un archivo.
    Args:
        authorization_response_url (str): La URL completa de respuesta de Google OAuth.
        redirect_uri (str): La URI de redirección que usaste para generar la URL de autenticación.
    Returns:
        bool: True si el intercambio fue exitoso, False en caso contrario.
    """
    state = session.get('oauth_state')
    if not state:
        print("Error: OAuth state no encontrado en la sesión. Posible CSRF o sesión perdida.")
        return False # Fallo de seguridad o sesión expirada

    flow = Flow.from_client_secrets_file(
        CLIENT_CONFIG_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri, 
        state=state # Se usa el 'state' para verificar la respuesta
    )
    try:
        flow.fetch_token(authorization_response=authorization_response_url)
        
        # Guarda las credenciales completas (incluido el refresh token) en la sesión
        token_info = flow.credentials.to_json()
        creds_dict = json.loads(token_info)

        # Añade client_id y client_secret a la información del token para futuras recargas
        creds_dict['client_id'] = flow.client_config['client_id']
        creds_dict['client_secret'] = flow.client_config['client_secret']
        creds_dict['scopes'] = SCOPES # Asegurarse de que los scopes estén guardados

        save_credentials_to_session(creds_dict)
        #save_credentials_to_file(CREDENTIALS_FILE, creds_dict) # Para persistencia entre sesiones del servidor
        
        return True
    except Exception as e:
        print(f"Error al intercambiar el código por token: {e}")
        return False
    
def exchange_code_for_token_cli(auth_code):
    """Intercambia el código de autorización por un token de acceso y un token de refresh para CLI."""
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_CONFIG_FILE, SCOPES,redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )
    try:
        token = flow.fetch_token(code=auth_code)
        if token:
            # Añadir client_id y client_secret al diccionario del token antes de guardarlo
            token['client_id'] = flow.client_config['client_id']
            token['client_secret'] = flow.client_config['client_secret']
        return token
    except Exception as e:
        print(f"Error al intercambiar el código por token: {e}")
        return None



def load_credentials_from_session() -> Credentials | None:
    """Carga las credenciales desde la sesión de Flask."""
    if 'credentials' in session:
        creds_info = session['credentials']
        try:
            # Reconstruye el objeto Credentials a partir del diccionario en la sesión
            creds = Credentials(
                token=creds_info.get('token'),
                refresh_token=creds_info.get('refresh_token'),
                token_uri=creds_info.get('token_uri'),
                client_id=creds_info.get('client_id'),
                client_secret=creds_info.get('client_secret'),
                scopes=creds_info.get('scopes')
            )
            return creds
        except Exception as e:
            print(f"Error al reconstruir credenciales de la sesión: {e}")
            session.pop('credentials', None) # Limpia credenciales corruptas de la sesión
            return None
    return None
def load_credentials_from_file(filename):
    """Carga las credenciales desde un archivo JSON."""
    creds = None
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            creds_info = json.load(file)
            token = creds_info.get('token')
            client_id = creds_info.get('client_id')
            client_secret = creds_info.get('client_secret')
            refresh_token = creds_info.get('refresh_token')
            token_uri = creds_info.get('token_uri')
            scopes = creds_info.get('scopes')

            if all([token,refresh_token, token_uri, client_id, client_secret, scopes]):
                creds = Credentials(
                    token=token,
                    refresh_token=refresh_token,
                    token_uri=token_uri,
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=scopes
                )
    return creds





def save_credentials_to_session(token_dict: dict):
    """Guarda las credenciales (diccionario de token) en la sesión de Flask."""
    session['credentials'] = token_dict
def save_credentials_to_file(filename, token):
    """Guarda las credenciales (incluido el refresh token) en un archivo JSON, creando el directorio si es necesario."""
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filename, 'w') as outfile:
        json.dump(token, outfile)
    # Crear google_ads_config.yaml
    config_data = {
        'developer_token': 'vhdX0LK2kgCZaAVFtG8fCg',  # ¡REEMPLAZA CON TU TOKEN REAL!
        'client_id': token.get('client_id'),
        'client_secret': token.get('client_secret'),
        'refresh_token': token.get('refresh_token'),
        'flow': 'installed_app',
        'use_proto_plus': True
    }

    config_file_path = os.path.join(os.path.dirname(filename), 'google_ads_config.yaml')
    with open(config_file_path, 'w') as yaml_file:
        yaml.dump(config_data, yaml_file)






def refresh_access_token(credentials):
    """Refresca el token de acceso si ha expirado (usando el refresh token)."""
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        return credentials
    return credentials
def refresh_access_token_cli(credentials):
    """Refresca el token de acceso si ha expirado (para CLI)."""
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        return credentials
    return credentials








def get_ads_client():
    """Crea un cliente de la API de Google Ads usando las credenciales."""
    return GoogleAdsClient.load_from_dict({
            "developer_token": DEVELOPER_TOKEN, # Reemplaza con tu token de desarrollador
            "json_key_file_path": CREDENTIALS_FILE,
            #"oauth2": {
            #    "client_id": credentials.client_id,
            #    "client_secret": credentials.client_secret,
            #    "refresh_token": credentials.refresh_token
            #},
            "use_proto_plus":True
    })


"""def get_ads_client():
    # Carga la configuración del YAML
    try:
        with open(GOOGLE_ADS_CONFIG_FILE, 'r') as f:
            google_ads_config = yaml.safe_load(f)
    except FileNotFoundError:
        raise Exception(f"Google Ads config file not found at {GOOGLE_ADS_CONFIG_FILE}")

    # Añade la ruta a la clave JSON de la Service Account
    google_ads_config['json_key_file_path'] = SERVICE_ACCOUNT_KEY_FILE

    # Inicializa el cliente de Google Ads con la configuración completa
    client = GoogleAdsClient.load_from_dict(google_ads_config)
    return client"""

def get_ads_client_cli(credentials):
    """Crea un cliente de la API de Google Ads usando las credenciales para CLI."""
    config_file_path = os.path.join(os.path.dirname(CREDENTIALS_FILE), 'google_ads_config.yaml')
    try:
        # Intenta cargar la configuración desde el archivo YAML
        client = GoogleAdsClient.load_from_storage(config_file_path)
        return client
    except Exception as e:
        print(f"Error al cargar la configuración de Google Ads desde YAML: {e}")
        return None





# ... (Funciones similares para la API de Looker Studio)
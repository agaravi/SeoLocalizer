from google.auth import default
from backend.utils.auth import *
import json
import urllib.parse


#BASE_DIR = os.path.dirname(__file__) # Obtiene el directorio base (backend)
#CREDENTIALS_FILE = os.path.join(BASE_DIR, 'config', 'google_ads_credentials.json')


  # 0. Autenticación
"""creds = load_credentials_from_file(CREDENTIALS_FILE)

if not creds or not creds.valid:
    authorization_url = generate_auth_url_cli()
    print(f"Por favor, visita la siguiente URL en tu navegador y autoriza la aplicación:\n{authorization_url}\n")
    auth_code = input("Introduce el código de autorización que recibiste: ")
    token = exchange_code_for_token_cli(auth_code)
    if token:
        save_credentials_to_file(CREDENTIALS_FILE, token)
        creds = load_credentials_from_file(CREDENTIALS_FILE)
    else:
        print("Error al obtener el token de acceso.")

if creds and creds.expired and creds.refresh_token:
    creds = refresh_access_token_cli(creds)
    save_credentials_to_file(CREDENTIALS_FILE, json.loads(creds.to_json()))

"""
def generate_looker_report(dataset_id, report_name,view_id):
    base_url = "https://lookerstudio.google.com/embed/reporting/create"
    #Para embeberlo https://lookerstudio.google.com/embed/reporting/create?parameters
    datasourceName=f"BQ{dataset_id}"

    # Parámetros para crear la copia del informe
    params ={
        "c.reportId":"aacd8641-ef79-451a-958c-af8890336b2d",
        "c.pageId":"a7OKF",
        "c.mode":"view",
        "r.reportName": report_name,
        "ds.datasourceName": datasourceName,
        "ds.connector": "bigQuery",
        "ds.type":"TABLE",
        "ds.projectId":"trabajofingrado-453708",
        "ds.datasetId":dataset_id,
        "ds.tableId":view_id,
        #"ds.sql":query
    }
    #"https://lookerstudio.google.com/reporting/aacd8641-ef79-451a-958c-af8890336b2d/page/a7OKF/edit"

    url_params = urllib.parse.urlencode(params)
    final_url = f"{base_url}?{url_params}"

    print("URL para ir al informe SEO final:")
    print(final_url)
    return final_url

"""generate_looker_report(
    dataset_id="negocio_20250514_133151_ab60ca9b",
    report_name="Informe duplicadoDobuss"
)"""
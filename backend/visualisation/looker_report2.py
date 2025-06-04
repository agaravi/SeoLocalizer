import os
import urllib.parse
import google.auth
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- Configuración de tu proyecto y reporte base ---
#PROJECT_NAME = os.environ.get("PROJECT_NAME")
PROJECT_NAME = "trabajofingrado-453708"
REPORT_ID="aacd8641-ef79-451a-958c-af8890336b2d"
#REPORT_ID = os.environ.get("REPORT_ID")

# Ruta al archivo JSON de la clave de la cuenta de servicio (¡AJUSTA ESTO!)
#SERVICE_ACCOUNT_KEY_FILE = "/etc/secrets/tfg-google-service-account-key.json"
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir)) # Subir dos niveles desde el script para llegar a la raíz del proyecto
SERVICE_ACCOUNT_KEY_FILE = os.path.join(project_root, "backend", "config", "tfg-google-service-account-key.json")


# --- Función para crear la fuente de datos programáticamente ---
def create_looker_studio_bigquery_datasource_programmatically(project_id, dataset_id, view_id, datasourceName):
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY_FILE,
            scopes=['https://www.googleapis.com/auth/datastudio',
                    'https://www.googleapis.com/auth/bigquery.readonly']
        )
        datastudio_service = build('datastudio', 'v1', credentials=credentials)

        datasource_body = {
            "displayName": datasourceName,
            "connector": {
                "connectorId": "bigQuery",
                "projectId": project_id,
                "datasetId": dataset_id,
                "tableId": view_id,
                "credentials": {
                    "type": "OWNER" # CRÍTICO: La cuenta de servicio es el propietario
                }
            }
        }

        print(f"Creando fuente de datos '{datasourceName}' para {dataset_id}.{view_id}...")
        request = datastudio_service.datasources().create(body=datasource_body)
        response = request.execute()
        print(f"Fuente de datos creada. ID: {response.get('name')}")
        return response.get('name') # Retorna el ID de la fuente de datos (ej. 'datasources/xxxxxxxxxxxx')

    except Exception as e:
        print(f"Error al crear la fuente de datos: {e}")
        return None

# --- Función principal para generar el informe de Looker Studio ---
def generate_looker_report(dataset_id, report_name, view_id):
    base_url = "https://lookerstudio.google.com/embed/reporting/create"

    # 1. Generar un nombre único para la fuente de datos (opcional, pero útil)
    datasourceName=f"BQ{dataset_id}"

    # 2. Crear la fuente de datos programáticamente con la cuenta de servicio como propietario
    datasource_id = create_looker_studio_bigquery_datasource_programmatically(
        PROJECT_NAME, dataset_id, view_id, datasourceName
    )

    if not datasource_id:
        print("No se pudo crear la fuente de datos. No se generará la URL del informe.")
        return None

    # Parámetros para crear la copia del informe
    params = {
        "c.reportId": REPORT_ID,
        "c.pageId": "a7OKF",
        "c.mode": "view",
        "r.reportName": report_name,
        # *** ESTOS PARÁMETROS SON CLAVE AHORA ***
        # Usamos la fuente de datos ya creada por la API
        "ds.dataSourceId": datasource_id
        # Los parámetros ds.datasourceName, ds.connector, ds.type, etc. ya NO son necesarios
        # porque estamos enlazando a una fuente de datos existente.
    }

    url_params = urllib.parse.urlencode(params)
    final_url = f"{base_url}?{url_params}"

    print("URL para ir al informe SEO final:")
    print(final_url)
    return final_url

def generate_looker_report2(dataset_id, report_name,view_id):
    base_url = "https://lookerstudio.google.com/embed/reporting/create"
    #Para embeberlo https://lookerstudio.google.com/embed/reporting/create?parameters
    datasourceName=f"BQ{dataset_id}"

    # Parámetros para crear la copia del informe
    params ={
        "c.reportId":REPORT_ID,
        "c.pageId":"a7OKF",
        "c.mode":"view",
        "c.explain":"false",
        "r.reportName": report_name,
        "ds.datasourceName": datasourceName,
        "ds.connector": "bigQuery",
        "ds.type":"TABLE",
        "ds.projectId":PROJECT_NAME,
        "ds.datasetId":dataset_id,
        "ds.tableId":view_id,
        #"ds.credentials.type":"OWNER" # CRÍTICO: La cuenta de servicio es el propietario
        #"ds.sql":query
    }

    url_params = urllib.parse.urlencode(params)
    final_url = f"{base_url}?{url_params}"

    print("URL para ir al informe SEO final:")
    print(final_url)
    return final_url

"""generate_looker_report(
    dataset_id="negocio_20250514_133151_ab60ca9b",
    report_name="Informe duplicadoDobuss"
)"""

# --- Ejemplo de uso (asegúrate de que SERVICE_ACCOUNT_KEY_FILE es correcto) ---
if __name__ == "__main__":
    # Asegúrate de reemplazar 'ruta/a/tu/clave-de-servicio.json'
    # con la ruta real al archivo JSON de tu cuenta de servicio.
    # También, asegúrate de que PROJECT_NAME y REPORT_ID están configurados en tus variables de entorno.
    
    # Ejemplo con IDs de prueba:
    # os.environ["PROJECT_NAME"] = "trabajofingrado-453708"
    # os.environ["REPORT_ID"] = "tu_id_de_informe_base_aqui" # Asegúrate de que este ID es real
    
    report_url = generate_looker_report2(
        dataset_id="negocio_20250604_115522_7d1cef47", # Reemplaza con tu dataset dinámico
        report_name="Informe Dinámico de Prueba",
        view_id="v_negocios_cleaned" # Reemplaza con tu vista dinámica
    )
    print(f"Informe generado en: {report_url}")
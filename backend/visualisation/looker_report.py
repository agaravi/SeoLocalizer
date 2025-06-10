import urllib.parse
import os

""" Genera una URL de Looker Studio que, al ser visitada, crea una copia de un informe plantilla
    y la conecta a un dataset/vista específico en Google BigQuery.

    Esta URL utiliza la "Linking API" de Looker Studio para automatizar la creación
    de informes personalizados para cada análisis."""

PROJECT_NAME=os.environ.get("PROJECT_NAME")
REPORT_ID=os.environ.get("REPORT_ID")

def generate_looker_report(dataset_id, report_name,view_id):
    base_url = "https://lookerstudio.google.com/embed/reporting/create"
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
        "ds.tableId":view_id
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
from backend.utils.auth import *
import urllib.parse
import os


PROJECT_NAME=os.environ.get("PROJECT_NAME")
REPORT_ID=os.environ.get("REPORT_ID")



def generate_looker_report(dataset_id, report_name,view_id):
    base_url = "https://lookerstudio.google.com/embed/reporting/create"
    #Para embeberlo https://lookerstudio.google.com/embed/reporting/create?parameters
    datasourceName=f"BQ{dataset_id}"

    # Parámetros para crear la copia del informe
    params ={
        "c.reportId":REPORT_ID,
        "c.pageId":"a7OKF",
        "c.mode":"view",
        "r.reportName": report_name,
        "ds.datasourceName": datasourceName,
        "ds.connector": "bigQuery",
        "ds.type":"TABLE",
        "ds.projectId":PROJECT_NAME,
        "ds.datasetId":dataset_id,
        "ds.tableId":view_id
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
from ingestion.scraping.main_scraper import scrape_local_directories
from ingestion.prueba_places import *
#from ingestion.SEO_validations import *
from ingestion.business_comparative import *  #DUDA
from ingestion.keywords.generacion import *
#from processing.traduction import *
from business.models import Business

from processing.natural_language import *
from visualisation.looker_report import *
#from utils.bigquery_client import save_to_bigquery
from utils.bigquery_client2 import *
from utils.auth import *
from flask import Flask, request, redirect, url_for, session
import os
import json
import threading
import time
#from config.settings import BIGQUERY_DATASET_ID

BASE_DIR = os.path.dirname(__file__) # Obtiene el directorio base (backend)
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'config', 'google_ads_credentials.json')

def main():

    # Introducir datos iniciales por consola
    nombre = input("Introduce el nombre del negocio (ejemplo: Gasolinera Repsol): ")
    categoría = input("Introduce la categoría (ejemplo: Restaurante): ")
    ciudad = input("Introduce la ciudad (ejemplo: Villa del Río): ")
    print("\n------------------------------------------------")

    # 0. Autenticación
    creds = load_credentials_from_file(CREDENTIALS_FILE)

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
            return

    if creds and creds.expired and creds.refresh_token:
        creds = refresh_access_token_cli(creds)
        save_credentials_to_file(CREDENTIALS_FILE, json.loads(creds.to_json()))

    client = get_ads_client_cli(creds)
    if not client:
        print("Error al inicializar el cliente de Google Ads.")
        return

    # 1. Creación del Main Business
    print("\n\n------------------------------------------------------------------------")
    print("MÓDULO DE EXTRACCIÓN DE DATOS")
    print("------------------------------------------------------------------------\n\n")
    place_id = get_google_places_data(nombre, ciudad,1)
    main_business = Business(place_id,True,categoría)
    place_data = get_details_main_place(place_id)
    main_business.set_from_google_places(place_data)

    # 2. Creación de los competidores
    competitors_ids=get_google_places_data(categoría,ciudad,5)
    competitors=[]
    for index, competitor_id in enumerate(competitors_ids, start=1):
        competitor_info=get_details_place(competitor_id)
        # Evitar duplicar el  ID del negocio principal
        if competitor_id == place_id:
            competitor_info["id"]=competitor_id+"competitor"       
        try:
            competitor = Business(competitor_info["id"],False,categoría)
            competitor.set_from_google_places(competitor_info)
            competitors.append(competitor)
            
            print(f"Competidor {index}: {competitor.nombre} - ID: {competitor.place_id}")
        except Exception as e:
            print(f"Error procesando competidor {competitor_id}: {str(e)}") 
    #print("\n\n------------------------------------------------------------------------")
    #print(competitors)
    #print("\n\n------------------------------------------------------------------------")        
    
    # 4. Traducir keywords y reviews
    #print(main_business)
    #print(competitors)
    print("\n\n------------------------------------------------------------------------")
    print("MÓDULO DE TRADUCCIÓN")
    print("------------------------------------------------------------------------\n\n")
    translate_businesses(main_business,competitors)
    #translate_keywords(main_business)
    #translate_reviews(main_business,competitors)
    #print("\n\n------------------------------------------------------------------------")
    #print(main_business)

    # 3. Comprobaciones y comparaciones
    print("\n\n------------------------------------------------------------------------")
    print("MÓDULO DE COMPROBACIONES")
    print("------------------------------------------------------------------------\n\n")
    
    main_business.validate_fields_and_completeness()
    comparison_data=compare_business(main_business,competitors)
    
    #print(main_business)
    #print("\n\n------------------------------------------------------------------------")
    
    main_business.set_comparison_data(comparison_data)
    
    #print(main_business)

    # Si el main business esta duplicado
    if main_business.top5 == True:
        for competitor in competitors:
            if competitor.place_id== place_id+"competitor":
                competitors.remove(competitor)
                del competitor



    # 5. Obtener sugerencias de palabras clave  
    print("\n\n------------------------------------------------------------------------")
    print("MÓDULO DE PALABRAS CLAVE")
    print("------------------------------------------------------------------------\n\n")
    main_business.set_keyword_suggestions(get_keyword_ideas(client,categoría, ciudad))
    #print("\n\n------------------------------------------------------------------------")
    #print(main_business)

    # 6. Análisis de sentimiento
    print("\n\n------------------------------------------------------------------------")
    print("MÓDULO DE ANÁLISIS DE SENTIMIENTO")
    print("------------------------------------------------------------------------\n\n")

    #hilo1 = threading.Thread(target=funcion_uno, args=("hilo_1",))
    #hilo2 = threading.Thread(target=funcion_dos, args=("hilo_2",))

    #hilo1.start()
    #hilo2.start()
    #hilo1.join()
    #hilo2.join()
    sentiment_analysis(main_business,competitors)

    # 7. Comprobación de citaciones locales (scrapeo)
    print("\n\n------------------------------------------------------------------------")
    print("MÓDULO DE SCRAPING")
    print("------------------------------------------------------------------------\n\n")
    citation_data=scrape_local_directories(main_business.nombre,main_business.direccion.ciudad,categoría,main_business.direccion.provincia,main_business.direccion.direccion_completa)
    main_business.set_citacions_data(citation_data)

    # 8. Almacenamiento en BigQuery
    print("\n\n------------------------------------------------------------------------")
    print("CREACIÓN DE LA BASE DE DATOS")
    print("------------------------------------------------------------------------\n\n")
    print
    bq_client = BigQueryClient()
    #bq_client.delete_dataset("trabajofingrado-453708.negocio_20250512_235600_4e49ee2f")
    #bq_client.delete_dataset("trabajofingrado-453708.negocio_20250519_120132_c90f787a")
    #bq_client.delete_dataset("trabajofingrado-453708.negocio_20250519_135536_069ffca2")
    #bq_client.delete_dataset("trabajofingrado-453708.negocio_20250514_111745_8e6af9b5")
    #bq_client.delete_dataset("trabajofingrado-453708.negocio_20250512_172422_1dffce5d")
    #bq_client.delete_dataset("trabajofingrado-453708.negocio_20250519_002311_7ca7b16a")

    dataset_id = bq_client.create_dataset()
    bq_client.create_table_with_schema(dataset_id,"Negocios")
    bq_client.upsert_business(dataset_id, "Negocios", main_business)
    for competitor in competitors:
        bq_client.upsert_business(dataset_id, "Negocios", competitor)
    
    # 9. Automatización de informes en Looker Studio
    print("\n\n------------------------------------------------------------------------")
    print("CREACIÓN DEL INFORME FINAL")
    print("------------------------------------------------------------------------\n\n")

    bq_client.create_normalized_view(dataset_id)
    url = generate_looker_report(dataset_id,"Informe "+nombre,"v_negocios_cleaned")

if __name__ == "__main__":
    main()
    #app.run(debug=True)

# app.py

from backend.ingestion.scraping.main_scraper import scrape_local_directories
from backend.ingestion.google_places import get_google_places_data,get_details_main_place,get_details_place
from backend.ingestion.business_comparative import compare_business  #DUDA
from backend.ingestion.keywords.keyword_generation import *
from backend.business.models import Business

from backend.processing.natural_language import sentiment_analysis
from backend.processing.google_traduction import translate_businesses
from backend.visualisation.looker_report import generate_looker_report
from backend.utils.bigquery_client import BigQueryClient
from backend.utils.auth import (
    exchange_code_for_token,
    load_credentials_from_session, get_ads_client
)
from flask import Flask, request, redirect, url_for, session, render_template, flash
import os
import threading

# --- Configuración de rutas de Flask ---
basedir = os.path.dirname(os.path.abspath(__file__))

template_dir = os.path.join(basedir, '..', 'frontend', 'templates')
static_dir = os.path.join(basedir, '..', 'frontend')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.urandom(24) # Clave secreta necesaria para la gestión de sesiones


# --- Rutas de la aplicación Flask ---

@app.route("/")
def inicio():
    """Ruta principal que muestra el formulario de entrada."""
    return render_template("index.html")

@app.route("/buscar", methods=['POST'])
def buscar():
    """
    Procesa los datos del formulario e inicia el análisis.
    """
    negocio_ciudad_input = request.form.get('negocio')
    categoria = request.form.get('keyword')

    if not all([negocio_ciudad_input, categoria]):
        flash("Por favor, rellena todos los campos.", "error")
        return redirect(url_for('inicio'))

    # El formato es "Nombre del negocio, Ciudad"
    parts = negocio_ciudad_input.split(',')
    if len(parts) < 2:
        flash("Formato de 'Nombre del negocio, ciudad' incorrecto. Por favor, asegúrate de incluir la ciudad separada por una coma.", "error")
        return redirect(url_for('inicio'))
    
    nombre = parts[0].strip()
    ciudad = ','.join(parts[1:]).strip() # Por si la ciudad tiene comas

    if not nombre or not ciudad:
        flash("No se pudo extraer el nombre del negocio o la ciudad. Asegúrate del formato 'Nombre del negocio, ciudad'.", "error")
        return redirect(url_for('inicio'))

    # Almacenar los datos del formulario temporalmente en la sesión
    # para poder recuperarlos después de la autenticación.
    session['temp_analysis_data'] = {'nombre': nombre, 'categoria': categoria, 'ciudad': ciudad}
    print("Información para comenzar el análisis: ")
    print(session['temp_analysis_data'])
    return _start_analysis(nombre, categoria, ciudad)

def _start_analysis(nombre, categoria, ciudad):
    """
    Función para iniciar el proceso de análisis en un hilo separado
    y redirigir a la página de carga.
    """
    app.config['analysis_results'] = {}     # Diccionario global simple en `app.config`
    analysis_id = str(os.urandom(16).hex()) # ID único para cada ejecución

    thread = threading.Thread(
        target=_run_analysis_in_background,
        args=(nombre, categoria, ciudad, analysis_id)
    )
    thread.start()

    # Redirige a una página de carga mientras el análisis se ejecuta
    return render_template("loading.html", analysis_id=analysis_id,nombre_negocio=session['temp_analysis_data']['nombre'])


@app.route("/analisis_SEO_<nombre>")
def analysis_status(analysis_id):
    """
    Esta ruta es consultada por el frontend para verificar el estado del análisis
    y recuperar la URL del informe de Looker Studio cuando esté listo.
    """
    result = app.config['analysis_results'].get(analysis_id)
    if result and not result.startswith("Error"):
        looker_studio_url = result.get('url')
        return render_template("results.html", looker_studio_url=looker_studio_url, analysis_id_to_delete=analysis_id)
    else:
        if result and result.startswith("Error"):
            return render_template("error.html", error_message=result), 500
        return "Análisis en progreso...", 202

def _run_analysis_in_background(nombre, categoria, ciudad, analysis_id):
    """Función auxiliar que envuelve `run_analysis` para ser ejecutada en un hilo."""
    try:
        url, dataset_id = run_analysis(nombre, categoria, ciudad)
        app.config['analysis_results'][analysis_id] = {'url': url, 'dataset_id': dataset_id}
        print(f"Análisis {analysis_id} completado. URL: {url}, Dataset ID: {dataset_id}")
    except Exception as e:
        app.config['analysis_results'][analysis_id] = f"Error en el análisis: {str(e)}"
        print(f"Error en el hilo de análisis para {analysis_id}: {str(e)}")

def run_analysis(nombre,categoría,ciudad):
    client = get_ads_client()
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
    print("Main Business:")
    print(main_business)

    # 2. Creación de los competidores
    competitors_ids=get_google_places_data(categoría,ciudad,5)
    if competitors_ids==[]:
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
    return url, dataset_id


@app.route("/cerrar/<analysis_id_to_delete>")
def cerrar(analysis_id_to_delete):
    print("\n\n------------------------------------------------------------------------")
    print("ELIMINACIÓN DE DATOS")
    print("------------------------------------------------------------------------\n\n")

    # 1. Eliminar el analysis_id de app.config['analysis_results']
    if analysis_id_to_delete in app.config['analysis_results']:
        analysis_info = app.config['analysis_results'].pop(analysis_id_to_delete)
        looker_studio_url = analysis_info.get('url')
        dataset_id = analysis_info.get('dataset_id')

        print(f"Eliminando datos para analysis_id: {analysis_id_to_delete}")
        print(f"URL de Looker Studio asociada: {looker_studio_url}")
        print(f"Dataset ID de BigQuery asociado: {dataset_id}")

        # 2. Eliminar el dataset de BigQuery
        if dataset_id:
            try:
                bq_client = BigQueryClient()
                bq_client.delete_dataset(dataset_id)
                print(f"Dataset de BigQuery '{dataset_id}' eliminado correctamente.")
            except Exception as e:
                print(f"Error al eliminar el dataset de BigQuery '{dataset_id}': {str(e)}")
        else:
            print("No se encontró un dataset_id para eliminar.")
    else:
        print(f"No se encontró el analysis_id '{analysis_id_to_delete}' en los resultados de análisis para eliminar.")

    # 3. Borrar los objetos Business y demás. De ello ya se encarga el recolector de basura.
    # Los objetos 'Business' (main_business y competitors) son locales a la función run_analysis
    # y se destruyen cuando la función termina, ya que a implementación actual no los guarda
    # globalmente más allá de BigQuery y la URL.

    # 4. Limpiar datos temporales de la sesión
    # Por ejemplo, si tienes 'temp_analysis_data' en la sesión al inicio, podrías borrarla:
    if 'temp_analysis_data' in session:
        del session['temp_analysis_data']
        print("Datos temporales de sesión 'temp_analysis_data' eliminados.")
    
    # Redirigir al inicio
    return redirect(url_for('inicio'))


# app.py

from backend.ingestion.scraping.main_scraper import scrape_local_directories
from backend.ingestion.google_places import get_google_places_data,get_details_main_place,get_details_place
from backend.ingestion.business_comparative import compare_business 
from backend.ingestion.keywords.keyword_generation import get_keyword_ideas
from backend.business.models import Business

from backend.processing.natural_language import sentiment_analysis
from backend.processing.google_traduction import translate_businesses
from backend.visualisation.looker_report2 import generate_looker_report
from backend.utils.bigquery_client import BigQueryClient
from backend.utils.auth import get_ads_client
from flask import Flask, jsonify, request, redirect, url_for, session, render_template, flash
import os
import threading
import re

# --- Configuración de rutas de Flask ---
basedir = os.path.dirname(os.path.abspath(__file__))

template_dir = os.path.join(basedir, '..', 'frontend', 'templates')
static_dir = os.path.join(basedir, '..', 'frontend')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.urandom(24) # Clave secreta necesaria para la gestión de sesiones

if 'analysis_results' not in app.config:
    app.config['analysis_results'] = {}     # Diccionario global simple en `app.config`
if 'business_name_to_analysis_id' not in app.config:
    app.config['business_name_to_analysis_id'] = {}

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
    session['temp_analysis_data'] = {'nombre': nombre, 'categoria': categoria, 'ciudad': ciudad}
    print("Información para comenzar el análisis: ")
    print(session['temp_analysis_data'])
    return _start_analysis(nombre, categoria, ciudad)

def _start_analysis(nombre, categoria, ciudad):
    """
    Función para iniciar el proceso de análisis en un hilo separado
    y redirigir a la página de carga.
    """
    analysis_id = str(os.urandom(16).hex()) # ID único para cada ejecución

    app.config['business_name_to_analysis_id'][nombre.lower()] = analysis_id

    thread = threading.Thread(
        target=_run_analysis_in_background,
        args=(nombre, categoria, ciudad, analysis_id)
    )
    thread.start()

    # Redirige a una página de carga mientras el análisis se ejecuta
    return render_template("loading.html", analysis_id=analysis_id,nombre_negocio=session['temp_analysis_data']['nombre'])

@app.route("/analysis_status/<analysis_id>")
def analysis_status(analysis_id):
    """
    Esta ruta es consultada por el frontend para verificar el estado del análisis
    y recuperar la URL del informe de Looker Studio cuando esté listo.
    Devuelve JSON con el estado.
    """
    result_info = app.config['analysis_results'].get(analysis_id)
    
    if result_info:
        if isinstance(result_info, str) and result_info.startswith("Error:"):
            redirect_url = url_for('display_seo_analysis_error', analysis_id=analysis_id)
            return jsonify({'status': 'error', 'redirect_url': redirect_url}), 200 # Devolver 200 para que el frontend lo procese
        elif isinstance(result_info, dict) and 'url' in result_info:
            nombre_negocio = None
            for name, id in app.config['business_name_to_analysis_id'].items():
                if id == analysis_id:
                    nombre_negocio = name
                    break

            if nombre_negocio:
                final_redirect_url = url_for('display_seo_analysis', nombre_negocio=nombre_negocio)
                return jsonify({'status': 'completed', 'redirect_url': final_redirect_url}), 200
    
    # Aún está en progreso
    return jsonify({'status': 'in_progress'}), 202

@app.route("/analisis_SEO_<nombre_negocio>")
def display_seo_analysis(nombre_negocio):
    """
    Esta ruta muestra el informe de Looker Studio final o la página de error.
    También se encarga de la limpieza de datos.
    """
    analysis_id = app.config['business_name_to_analysis_id'].get(nombre_negocio.lower())

    if not analysis_id:
        # Si no se encuentra un analysis_id para este nombre, es un error 404 o sesión expirada
        return render_template("error.html", error_message=f"No se encontró un análisis activo. La sesión pudo haber expirado o el análisis no se inició correctamente."), 404

    result_info = app.config['analysis_results'].get(analysis_id)

    # ------ LIMPIEZA DE DATOS-----
    # Limpiar los datos de app.config después de obtener el resultado,
    # ya que se va a mostrar la página final, ya sea de éxito o error.
    #if analysis_id in app.config['analysis_results']:
    #    del app.config['analysis_results'][analysis_id]
    #if nombre_negocio.lower() in app.config['business_name_to_analysis_id']:
    #    del app.config['business_name_to_analysis_id'][nombre_negocio.lower()]
    
    if result_info:
        if isinstance(result_info, dict) and 'url' in result_info:
            # Si el análisis está listo, renderiza el informe
            looker_studio_url = result_info.get('url')
            # Pasamos analysis_id para el botón de cerrar
            return render_template("results.html", looker_studio_url=looker_studio_url, analysis_id_to_delete=analysis_id)
        else:
            # Si es un error, renderiza la página de error
            error_message = "El análisis no está listo o ha ocurrido un error inesperado al cargar el informe."
        if result_info and isinstance(result_info, str) and result_info.startswith("Error:"):
            error_message = result_info.replace("Error: ", "")
            return render_template("error.html", error_message=error_message), 500

@app.route("/analysis_error/<analysis_id>")
def display_seo_analysis_error(analysis_id):
    """
    Ruta de error genérica para cuando no se puede determinar un nombre de negocio para la URL de error,
    o en casos de errores muy tempranos.
    """
    error_message = "Ha ocurrido un error inesperado durante el análisis. Por favor, inténtalo de nuevo."
    
    # Detectar los distintos errores en el análisis
    if analysis_id not in ["no-id-found", "network-error-from-js", "initial-data-missing"]:
        result_info = app.config['analysis_results'].get(analysis_id)
        if result_info and isinstance(result_info, str) and result_info.startswith("Error:"):
            error_message = result_info.replace("Error: ", "")
        elif not result_info:
            error_message = f"No se encontraron detalles del error para el análisis. El análisis pudo haber expirado o ya fue procesado."
    else: 
        if analysis_id == "no-id-found":
            error_message = "No se pudieron obtener los datos de inicio del análisis. La página de carga no pudo iniciarse correctamente."
        elif analysis_id == "network-error-from-js":
            error_message = "Hubo un problema de conexión con el servidor mientras se realizaba el análisis. Por favor, revisa tu conexión a internet."
        elif analysis_id == "initial-data-missing": 
            error_message = "Los datos iniciales necesarios para el análisis no se encontraron. Por favor, inténtalo de nuevo."

    # Limpiar el análisis si se encontró, aunque el nombre del negocio no esté claro
    if analysis_id in app.config['analysis_results']:
        del app.config['analysis_results'][analysis_id]
    # Intentar limpiar el mapeo si el analysis_id aún está en business_name_to_analysis_id
    for name, an_id in list(app.config['business_name_to_analysis_id'].items()):
        if an_id == analysis_id:
            del app.config['business_name_to_analysis_id'][name]
            break

    return render_template("error.html", error_message=error_message), 500

def _run_analysis_in_background(nombre, categoria, ciudad, analysis_id):
    """Función auxiliar que envuelve `run_analysis` para ser ejecutada en un hilo."""
    try:
        url, dataset_id = run_analysis(nombre, categoria, ciudad)
        app.config['analysis_results'][analysis_id] = {'url': url, 'dataset_id': dataset_id, 'nombre_negocio': nombre}
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


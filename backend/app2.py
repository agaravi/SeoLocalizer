# app.py

from ingestion.scraping.main_scraper import scrape_local_directories
from ingestion.prueba_places import *
from ingestion.business_comparative import *  #DUDA
from ingestion.keywords.generacion import *
#from processing.traduction import *
from business.models import Business

from processing.natural_language import *
from visualisation.looker_report import *
#from utils.bigquery_client import save_to_bigquery
from utils.bigquery_client2 import *
from utils.auth import *
from flask import Flask, request, redirect, url_for, session, render_template, flash
import os
import json
import threading
# Importa las funciones de autenticación
from utils.auth import (
    generate_auth_url, exchange_code_for_token,
    load_credentials_from_session, save_credentials_to_session,
    load_credentials_from_file, save_credentials_to_file,
    refresh_access_token
)
# Importa tu lógica de análisis
#from run_analysis_module import run_analysis 

basedir = os.path.dirname(os.path.abspath(__file__))

# --- Configuración de Flask ---
# Navegamos 'hacia arriba' desde backend/ y luego 'hacia abajo' a frontend/
template_dir = os.path.join(basedir, '..', 'frontend', 'templates')
static_dir = os.path.join(basedir, '..', 'frontend')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.urandom(24) # ¡Clave secreta necesaria para la gestión de sesiones!

# Rutas a tus archivos de configuración
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'google_ads_credentials.json')
CLIENT_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'oauth2_credentials.json') 

# Variable para almacenar los datos del formulario mientras se gestiona la autenticación
# En un entorno de producción, considera usar una base de datos o Redis para esto
temp_form_data = {}

# --- Rutas de la Aplicación Flask ---

@app.route("/")
def inicio():
    """Ruta principal que muestra el formulario de entrada."""
    return render_template("index.html")

@app.route("/buscar", methods=['POST'])
def buscar():
    """
    Procesa los datos del formulario.
    Verifica las credenciales y, si no son válidas, inicia el flujo de autenticación.
    Si son válidas, inicia el análisis.
    """
    negocio_ciudad_input = request.form.get('negocio')
    categoria = request.form.get('keyword') # Ahora se llama 'keyword' en tu HTML

    if not all([negocio_ciudad_input, categoria]):
        flash("Por favor, rellena todos los campos.", "error")
        return redirect(url_for('inicio'))

    # --- PARSEAR EL CAMPO 'negocio_ciudad_input' ---
    # Asumimos que el formato es "Nombre del Negocio, Ciudad"
    parts = negocio_ciudad_input.split(',')
    if len(parts) < 2:
        flash("Formato de 'Nombre del Negocio, ciudad' incorrecto. Por favor, asegúrate de incluir la ciudad separada por una coma.", "error")
        return redirect(url_for('inicio'))
    
    nombre = parts[0].strip()
    ciudad = ','.join(parts[1:]).strip() # Si la ciudad tiene comas (ej. "Nueva York, NY")

    if not nombre or not ciudad:
        flash("No se pudo extraer el nombre del negocio o la ciudad. Asegúrate del formato 'Nombre del Negocio, ciudad'.", "error")
        return redirect(url_for('inicio'))

    # Almacena los datos del formulario temporalmente en la sesión
    # para poder recuperarlos después de la autenticación.
    session['temp_analysis_data'] = {'nombre': nombre, 'categoria': categoria, 'ciudad': ciudad}

    creds = load_credentials_from_session()

    # Si no hay credenciales en la sesión, intenta cargarlas desde el archivo
    if not creds:
        creds = load_credentials_from_file(CREDENTIALS_FILE)
        if creds:
            # Si se cargan desde el archivo, guárdalas en la sesión para uso futuro
            save_credentials_to_session(json.loads(creds.to_json()))

    # --- Lógica de verificación y refresco de credenciales ---
    # Esto se hará antes de decidir si necesitamos redirigir a autenticar
    if creds and creds.expired and creds.refresh_token:
        try:
            creds = refresh_access_token(creds)
            # Actualiza la sesión con las credenciales refrescadas
            save_credentials_to_session(json.loads(creds.to_json()))
            # También guarda en el archivo para persistencia a largo plazo
            save_credentials_to_file(CREDENTIALS_FILE, json.loads(creds.to_json()))
        except Exception as e:
            flash(f"Error al refrescar el token de acceso: {e}. Por favor, autentícate de nuevo.", "error")
            # Si falla el refresco, las credenciales no son válidas, se irá al flujo de autenticación
            creds = None # Forzar que se considere inválido y pida autenticación

    # Si las credenciales no son válidas o no existen, redirige a la autenticación
    if not creds or not creds.valid:
        flash("Necesitas autenticarte con Google Ads.", "warning")
        redirect_uri = url_for('oauth2callback', _external=True)
        auth_url = generate_auth_url(redirect_uri)
        return redirect(auth_url)
    
    # Si las credenciales son válidas, continúa directamente al análisis
    return _start_analysis(nombre, categoria, ciudad, creds)


@app.route("/oauth2callback")
def oauth2callback():
    """
    Maneja la llamada de retorno de Google después de la autenticación.
    Intercambia el código de autorización por un token de acceso y lo guarda.
    Después de la autenticación, reanuda el análisis.
    """
    redirect_uri = url_for('oauth2callback', _external=True)
    if exchange_code_for_token(request.url, redirect_uri):
        flash("Autenticación con Google Ads exitosa. Reanudando análisis...", "success")
        
        # Recupera los datos del formulario almacenados en la sesión
        analysis_data = session.pop('temp_analysis_data', None)
        
        if analysis_data:
            nombre = analysis_data['nombre']
            categoria = analysis_data['categoria']
            ciudad = analysis_data['ciudad']
            creds = load_credentials_from_session() # Vuelve a cargar las credenciales, que ya deberían estar en la sesión

            if creds and creds.valid:
                return _start_analysis(nombre, categoria, ciudad, creds)
            else:
                flash("Error: Las credenciales no son válidas después de la autenticación.", "error")
                return redirect(url_for('inicio'))
        else:
            flash("Error: No se encontraron datos de análisis previos. Intenta de nuevo.", "error")
            return redirect(url_for('inicio'))
    else:
        flash("Error durante la autenticación con Google Ads.", "error")
        return redirect(url_for('inicio'))

def _start_analysis(nombre, categoria, ciudad, creds):
    """
    Función interna para iniciar el proceso de análisis en un hilo separado
    y redirigir a la página de carga.
    """
    # Usaremos un diccionario global simple en `app.config` para la demostración.
    app.config['analysis_results'] = {}
    analysis_id = str(os.urandom(16).hex()) # ID único para esta ejecución

    thread = threading.Thread(
        target=_run_analysis_in_background,
        args=(nombre, categoria, ciudad, creds, analysis_id)
    )
    thread.start()

    # Redirige a una página de carga mientras el análisis se ejecuta
    return render_template("loading.html", analysis_id=analysis_id)


@app.route("/analysis_status/<analysis_id>")
def analysis_status(analysis_id):
    """
    Esta ruta es consultada por el frontend para verificar el estado del análisis
    y recuperar la URL del informe de Looker Studio cuando esté listo.
    """
    result = app.config['analysis_results'].get(analysis_id)
    if result:
        # Una vez que se recupera el resultado, se limpia de la memoria
        del app.config['analysis_results'][analysis_id]
        return render_template("results.html", looker_studio_url=result)
    else:
        return "Análisis en progreso...", 202 

def _run_analysis_in_background(nombre, categoria, ciudad, creds, analysis_id):
    """Función auxiliar que envuelve `run_analysis` para ser ejecutada en un hilo."""
    try:
        # Asegúrate de que `run_analysis` es robusta y maneja sus propias excepciones
        looker_studio_url = run_analysis(nombre, categoria, ciudad, creds)
        app.config['analysis_results'][analysis_id] = looker_studio_url
    except Exception as e:
        app.config['analysis_results'][analysis_id] = f"Error en el análisis: {str(e)}"
        print(f"Error en el hilo de análisis para {analysis_id}: {str(e)}")

def run_analysis(nombre,categoría,ciudad,creds):
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
    return url

# --- Ejecución de la Aplicación Flask ---
#if __name__ == "__main__":
    #app.run(debug=True)
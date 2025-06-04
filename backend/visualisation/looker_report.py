import urllib.parse
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service # Importar Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException



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
        "c.explain":"false",
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


    
    # --- Configuración de Selenium ---
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Ejecutar en modo sin interfaz gráfica
    options.add_argument("--no-sandbox") # Necesario para entornos Linux sin sandbox
    options.add_argument("--disable-dev-shm-usage") # Reduce el uso de memoria en contenedores
    options.add_argument("--window-size=1920,1080") # Asegura una ventana grande para que los elementos sean visibles

    # --- ATENCIÓN: Gestión de la sesión de Google ---
    # Este es el punto más complejo para Render.
    # No hay una forma sencilla y segura de reusar perfiles de Chrome localmente creados en Render.
    # La autenticación manual a través de Selenium es propensa a CAPTCHAs y bloqueos.
    # Considera:
    # 1. Ejecutar esto localmente con tu perfil logueado y luego subir el informe generado. (No es automático para cada informe)
    # 2. Si Looker Studio permite la creación sin login persistente (solo para la sesión), probar así.
    # 3. Si Render tiene alguna solución de "perfil de navegador" pre-logueado (poco probable).
    # 4. **La opción de la que hablamos: si tu cuenta de agaravi3535 tiene un nivel de privilegio tan alto (Propietario de GCP) que Looker Studio procesa la URL de `create` *automáticamente* cuando se abre en un navegador limpio (sin perfil persistente), entonces este script podría funcionar sin un perfil especial.** Esto es lo que queremos probar.

    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        
        # Pasa el objeto Service y las opciones al constructor de Chrome
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(90)

        print(f"Navegando a la URL de creación del informe: {final_url}")
        driver.get(final_url)

        # --- Espera y detección de éxito/falla ---
        # 1. Esperar por el cambio de URL (el ID del informe en la URL cambia después de la duplicación)
        try:
            print("Esperando cambio de URL...")
            WebDriverWait(driver, 60).until(
                EC.url_changes(final_url)
            )
            print(f"URL cambió a: {driver.current_url}")
        except TimeoutException:
            print("Error: El cambio de URL no ocurrió en el tiempo esperado.")
            driver.save_screenshot("screenshot_url_change_timeout.png")
            # Intentar detectar el modal de error si no hubo cambio de URL
            try:
                error_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "material-dialog-button-ok"))
                )
                error_text = driver.find_element(By.CSS_SELECTOR, "div[id='alert-dialog-message']").text
                print(f"Se detectó un modal de error de Looker Studio: {error_text}")
                driver.save_screenshot("screenshot_looker_studio_error_modal.png")
                return None
            except TimeoutException:
                print("No se detectó modal de error después de timeout de URL.")
            return None

        # 2. Una vez que la URL ha cambiado, esperar que el contenido del informe sea visible
        # Los selectores pueden ser muy específicos y cambiar. Inspecciona tu informe real.
        # Aquí hay algunos intentos comunes para el canvas principal del informe.
        try:
            print("Esperando que el informe se cargue y sea visible...")
            WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.report-canvas, [data-testid='report-content'], .report-page"))
            )
            print("Informe cargado exitosamente.")
            final_report_url = driver.current_url
            print(f"URL final del informe creado: {final_report_url}")
            return final_report_url
            
        except TimeoutException:
            print("Error: El contenido del informe no se hizo visible en el tiempo esperado.")
            driver.save_screenshot("screenshot_content_timeout.png")
            return None
        except NoSuchElementException:
            print("Error: No se encontró el elemento esperado del informe.")
            driver.save_screenshot("screenshot_element_not_found.png")
            return None

    except Exception as e:
        print(f"Error general en Selenium: {e}")
        if driver:
            driver.save_screenshot("screenshot_general_selenium_error.png")
        return None
    finally:
        if driver:
            driver.quit() # Asegurarse de cerrar el navegador
    #print("URL para ir al informe SEO final:")
    #print(final_url)
    #return final_url

"""generate_looker_report(
    dataset_id="negocio_20250514_133151_ab60ca9b",
    report_name="Informe duplicadoDobuss"
)"""
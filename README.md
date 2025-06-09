# 📈 SEOLocalizer: Potencia tu SEO Local con Análisis Automatizado

[![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask Version](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Introducción

**SEOLocalizer** es una aplicación web innovadora diseñada para transformar la gestión del SEO local de cualquier negocio. Automatiza la extracción, procesamiento, análisis y visualización de datos cruciales de perfiles de Google Business Profile y otros directorios locales. El objetivo principal es proporcionar a las empresas información estratégica y accionable para mejorar su posicionamiento en búsquedas locales y su reputación online.

Desde la recolección de reseñas y datos de perfil hasta la generación de ideas de palabras clave y análisis de sentimiento, SEOLocalizer centraliza y simplifica el proceso de optimización local.

## ✨ Características Principales

* **Extracción de Datos de Google Places:** Recopila información detallada del perfil de Google Business Profile del negocio principal y de sus principales competidores (nombre, dirección, teléfono, sitio web, fotos, valoraciones, categorías, reseñas).
* **Análisis Comparativo:** Compara el negocio principal con sus competidores en métricas clave como número de fotos y reseñas, e identifica oportunidades de mejora en la completitud del perfil.
* **Generación de Palabras Clave:** Utiliza la API de Google Ads para sugerir palabras clave relevantes basadas en la categoría y ubicación del negocio, filtrando por competencia y volumen de búsqueda.
* **Análisis de Sentimiento de Reseñas:** Procesa las reseñas de Google utilizando Google Cloud Natural Language API para identificar la connotación (positiva/negativa) y la magnitud del sentimiento, así como las palabras clave más frecuentes.
* **Traducción de Contenido:** Traduce reseñas y categorías a un idioma consistente (español) utilizando Google Cloud Translation API para un análisis unificado.
* **Scraping de Directorios Locales:** Rastrea directorios online como Firmania, InfoisInfo, Habitissimo y Páginas Amarillas (vía Zyte API) para verificar la consistencia de la información del negocio (NAP - Nombre, Dirección, Teléfono) y detectar inconsistencias o ausencias.
* **Almacenamiento Persistente en BigQuery:** Almacena todos los datos procesados y analizados en Google BigQuery, una base de datos analítica escalable, creando un dataset y una vista normalizada por cada análisis.
* **Generación de Informes Dinámicos en Looker Studio:** Genera automáticamente URLs de informes preconfiguradas en Looker Studio para una visualización interactiva y en tiempo real de los resultados del análisis.
* **Descarga de Informes PDF:** Permite la descarga de un informe SEO detallado en formato PDF.
* **Eliminación Automática de Datos:** Los datos sensibles del análisis (dataset en BigQuery) se eliminan automáticamente al cerrar el informe para garantizar la privacidad y optimizar recursos.

## 🛠️ Tecnologías Utilizadas

### Backend y Desarrollo
* **Lenguaje de Programación:** Python 3.9+
* **Framework Web:** Flask
* **Gestor de Paquetes:** pip
* **Librerías Python Clave:**
    * `requests`: Para solicitudes HTTP.
    * `BeautifulSoup4` (`bs4`): Parsing HTML.
    * `dataclasses`, `typing`: Modelado de datos estructurado.
    * `unicodedata`, `re`, `difflib`, `urllib.parse`: Normalización y manejo de texto/URLs.
    * `pytest`: Framework para pruebas unitarias.
    * `unittest.mock`: Para simulación (mocking) en tests.

### Servicios Cloud y APIs
* **Google Cloud Platform (GCP):**
    * **Google Places API:** Datos de negocios y reseñas.
    * **Google Ads API:** Ideas de palabras clave.
    * **Google Cloud Translation API:** Traducción de texto.
    * **Google Cloud Natural Language API:** Análisis de sentimiento y entidades.
    * **Google BigQuery:** Almacenamiento de datos analíticos.
    * **Looker Studio:** Visualización de informes.
* **Zyte API:** Servicio de scraping para directorios locales.

### Frontend
* **HTML:** Estructura de las páginas web.
* **CSS:** Estilos (con archivos separados para estilos generales y de carga).
* **JavaScript:** Lógica de interactividad, validación de formularios y gestión de la página de carga.

## 📂 Estructura del Proyecto

El proyecto sigue una arquitectura modular, dividida en `backend` y `frontend`, con el objetivo de separar claramente las responsabilidades y facilitar el desarrollo y mantenimiento.

.
├── backend/                                   # Lógica del servidor y procesamiento de datos
│   ├── business/                              # Modelos de negocio y esquemas de BigQuery
│   │   ├── init.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── ingestion/                             # Recolección de datos de fuentes externas
│   │   ├── init.py
│   │   ├── business_comparative.py            # Lógica de comparación de negocios
│   │   ├── google_places/                     # Interacción con Google Places API
│   │   │   ├── init.py
│   │   │   └── google_places.py
│   │   ├── keywords/                          # Generación de palabras clave
│   │   │   ├── init.py
│   │   │   └── keyword_generation.py
│   │   └── scraping/                          # Scraping de directorios locales (vía Zyte API)
│   │       ├── init.py
│   │       ├── normalizations.py              # Funciones de normalización de texto
│   │       ├── Zyte_Firmania_scraper.py
│   │       ├── Zyte_Habitissimo_scraper.py
│   │       ├── Zyte_InfoisInfo_scraper.py
│   │       ├── Zyte_PaginasAmarillas_scraper.py
│   │       └── main_scraper.py                # Main del scraping
│   ├── processing/                            # Procesamiento y análisis de datos
│   │   ├── init.py
│   │   ├── data_transformation.py
│   │   ├── google_traduction.py               # Traducción de texto
│   │   └── natural_language.py                # Análisis de lenguaje natural 
│   ├── utils/                                 # Utilidades generales y clientes de servicios
│   │   ├── init.py
│   │   ├── auth.py                            # Gestión de autenticación
│   │   └── bigquery_client.py                 # Interacción con BigQuery
│   ├── visualisation/                         # Generación de informes
│   │   ├── init.py
│   │   └── looker_report.py                      # Generación de URLs de Looker Studio
│   ├── app.py                                 # Punto de entrada principal de la aplicación Flask
│   └── tests/                                 # Pruebas unitarias
│       └── init.py                            # (y otros archivos test_*.py, ejecutar_tests.py)
├── frontend/                                  # Interfaz de usuario y lógica cliente
│   ├── css/                                   # Hojas de estilo CSS
│   │   ├── loading.css
│   │   └── style.css
│   ├── js/                                    # Scripts JavaScript
│   │   ├── loading.js
│   │   └── script.js
│   ├── resources/                             # Archivos estáticos (imágenes, etc.)
│   │   └── logo.jpg                        
│   └── templates/                             # Plantillas HTML renderizadas por Flask
│       ├── error.html
│       ├── index.html
│       ├── loading.html
│       └── results.html
├── requirements.txt                           # Lista de dependencias de Python
└── README.md                                  # Este archivo

Los archivos `__init__.py` marcan los directorios como paquetes Python, permitiendo la importación modular y la organización jerárquica del código.

## 🧪 Pruebas

El proyecto incluye un conjunto de pruebas unitarias para asegurar la fiabilidad y el correcto funcionamiento de los componentes individuales.

1.  **Ejecutar Tests:**
    Desde la raíz del proyecto, ejecuta el script de tests:
    ```bash
    python ejecutar_tests.py
    ```
    Este script utilizará `pytest` para descubrir y ejecutar todas las pruebas, mostrando un resumen detallado en la terminal.

## ⚠️ Problemas Conocidos

* **Acceso a Informes de Looker Studio para Usuarios Finales:** Los usuarios que no sean propietarios del proyecto de Google Cloud pueden experimentar dificultades para visualizar los informes de Looker Studio generados automáticamente a través de la URL de "creación" (`.../reporting/create?parameters`). Esto se debe a que Looker Studio, al intentar crear la fuente de datos en nombre del usuario final, requiere permisos de `BigQuery Data Viewer` para ese usuario sobre el dataset y la vista subyacentes, lo cual no siempre es posible sin una configuración de permisos a nivel de organización o credenciales específicas para cada usuario. Las URLs generadas funcionan correctamente para los propietarios del proyecto o cuando se acceden de forma directa (copiando y pegando en el navegador tras una primera carga), pero la redirección automática desde la aplicación puede fallar para otros usuarios.


from google.cloud import bigquery
from datetime import datetime
import random
import uuid
import os
import json
#from processing import data_transformation
from backend.business.schemas import Schemas
from backend.business.models import Business

class BigQueryClient:
    def __init__(self):
        self._init_client()
        
    def _init_client(self):
        """Configura el cliente de BigQuery con las credenciales."""
        key_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "../config/tfg-google-service-account-key.json"
        )
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/tfg-google-service-account-key.json"
        self.client = bigquery.Client()

    # --- Operaciones básicas de datasets/tablas ---
    def create_dataset(self, dataset_id=None):
        """Crea un dataset con ID único si no se proporciona uno."""
        dataset_id = dataset_id or self._generate_dataset_id()
        try:
            dataset_ref = self.client.dataset(dataset_id)
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "EU"
            self.client.create_dataset(dataset, exists_ok=True)
            return dataset_id
        except Exception as e:
            print(f"Error creando dataset: {e}")
            return

    def create_table(self, dataset_id, table_name, schema):
        """Crea una tabla con el esquema especificado."""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_name)
            table = bigquery.Table(table_ref, schema=schema)
            self.client.create_table(table, exists_ok=True)
            return True
        except Exception as e:
            print(f"Error creando tabla: {e}")
            return False
    
    def create_table_with_schema(self, dataset_id, table_name):
        """Crea una tabla con el esquema predefinido"""
        schema = Schemas.get_table_schema(table_name)
        if not schema:
            raise ValueError(f"Esquema no definido para la tabla {table_name}")
            
        return self.create_table(dataset_id, table_name, schema)
    
    def delete_dataset(self, dataset_id):
        """Elimina un dataset específico por ID (incluyendo su contenido)."""
        try:
            self.client.delete_dataset(
                dataset_id,
                delete_contents=True,
                not_found_ok=True
            )
            print(f"Dataset '{dataset_id}' eliminado correctamente.")
            return True
        except Exception as e:
            print(f"Error al eliminar el dataset '{dataset_id}': {e}")
            return False

    def delete_all_datasets(self):
        """Elimina todos los datasets del proyecto"""
        try:
            datasets = list(self.client.list_datasets())
            if not datasets:
                print("No se encontraron datasets.")
                return

            for dataset in datasets:
                dataset_id = dataset.dataset_id
                print(f"Eliminando dataset: {dataset_id}")
                self.client.delete_dataset(
                    dataset_id,
                    delete_contents=True,  # Borra también todas las tablas
                    not_found_ok=True
                )
            print("Todos los datasets han sido eliminados.")
        except Exception as e:
            print(f"Error al eliminar datasets: {e}")

    # --- Operaciones de datos ---
    def execute_query(self, query, params=None):  #NO SE DEBERIA USAR
        """Ejecuta una consulta SQL con parámetros opcionales."""
        job_config = bigquery.QueryJobConfig()
        if params:
            job_config.query_parameters = params
        return self.client.query(query, job_config=job_config).result()

    def insert_rows(self, dataset_id, table_id, rows):
        """Inserta filas en una tabla."""
        table_ref = self.client.dataset(dataset_id).table(table_id)
        table = self.client.get_table(table_ref)
        return self.client.insert_rows_json(table, rows)

    def upsert_business(self, dataset_id, table_name, business: Business):
        """Inserta o actualiza un negocio completo"""
        try:
            table_ref = self.client.dataset(dataset_id).table(table_name)
            table = self.client.get_table(table_ref)
            
            # Convertir a formato BigQuery (excluyendo None)
            row = business.to_bigquery_format()
            #print(row)
            # Solo continuar si tenemos campos para actualizar/insertar
            if not row:
                print("No hay datos válidos para upsert")
                return False
                
            # Preparar parámetros de consulta
            query_parameters = []
            update_fields = []
            
            for key, valor in row.items():
                # Manejo especial para algunos tipos
                #print(key)
                #print(valor)
                if key == "palabras_clave":
                    #print("hola")
                    palabras_params = [
                        bigquery.StructQueryParameter(
                            None,
                            bigquery.ScalarQueryParameter("keyword", "STRING", p.get("keyword")),
                            bigquery.ScalarQueryParameter("indice_competicion", "INT64", p.get("indice_competicion")),
                            bigquery.ScalarQueryParameter("busquedas_mensuales", "INT64", p.get("busquedas_mensuales"))
                        ) for p in valor
                    ]
                    #print(palabras_params)
                    param = bigquery.ArrayQueryParameter(key, "RECORD", palabras_params)
                    #print(param)

                elif isinstance(valor, list):
                    #print(valor)
                    param = bigquery.ArrayQueryParameter(
                        key, 
                        "STRING" if all(isinstance(p, str) for p in valor) else "JSON", 
                        valor
                    )
                    #print(param)

                else:
                    param = bigquery.ScalarQueryParameter(
                        key, 
                        self.inferir_tipo(valor), 
                        valor
                    )
                    #print(param)
                query_parameters.append(param)
                update_fields.append(f"{key}=@{key}")
            
            # Construir consulta MERGE dinámica
            columns = ', '.join(row.keys())
            placeholders = ', '.join([f'@{k}' for k in row.keys()])
            updates = ', '.join(update_fields)
            
            query = f"""
                MERGE `{dataset_id}.{table_name}` tabla
                USING (SELECT @place_id as place_id) S
                ON tabla.place_id = S.place_id
                WHEN MATCHED THEN
                    UPDATE SET {updates}
                WHEN NOT MATCHED THEN
                    INSERT ({columns}) VALUES ({placeholders})
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=query_parameters
            )
            
            self.client.query(query, job_config=job_config).result()
            return True   
        except Exception as e:
            print(f"Error en upsert: {str(e)}")
            return False
        
    # --- Operaciones de vista ---
    def create_normalized_view(self, dataset_id, source_table="Negocios", view_name="v_negocios_cleaned"):
        """
        Crea o reemplaza una vista normalizada a partir de la tabla de negocios.
        Convierte campos potencialmente conflictivos como n_fotos_media y n_reviews_media.
        """
        try:
            view_id = f"{self.client.project}.{dataset_id}.{view_name}"

            query = f"""
            CREATE OR REPLACE VIEW `{view_id}` AS
            SELECT
                CAST(place_id AS STRING) AS place_id,
                CAST(main_business AS BOOL) AS main_business,
                CAST(nombre AS STRING) AS nombre,
                CAST(palabra_busqueda AS STRING) AS palabra_busqueda,
                CAST(direccion_completa AS STRING) AS direccion_completa,
                CAST(telefono_nacional AS STRING) AS telefono_nacional,
                CAST(telefono_internacional AS STRING) AS telefono_internacional,
                CAST(website AS STRING) AS website,
                CAST(n_fotos AS INT64) AS n_fotos,
                CAST(calle AS STRING) AS calle,
                CAST(ciudad AS STRING) AS ciudad,
                CAST(provincia AS STRING) AS provincia,
                CAST(codigo_postal AS STRING) AS codigo_postal,
                CAST(pais AS STRING) AS pais,
                CAST(valoracion_media AS FLOAT64) AS valoracion_media,
                CAST(n_valoraciones AS INT64) AS n_valoraciones,
                CAST(categoria_principal AS STRING) AS categoria_principal,
                CAST(categoria_principal_nombre AS STRING) AS categoria_principal_nombre,
                categorias_secundarias,
                CAST(estado_negocio AS STRING) AS estado_negocio,
                CAST(sin_local_fisico AS BOOL) AS sin_local_fisico,
                CAST(horario_normal AS BOOL) AS horario_normal,
                CAST(horario_festivo AS BOOL) AS horario_festivo,
                CAST(tiene_nombre AS BOOL) AS tiene_nombre,
                CAST(tiene_direccion AS BOOL) AS tiene_direccion,
                CAST(tiene_telefono AS BOOL) AS tiene_telefono,
                CAST(tiene_website AS BOOL) AS tiene_website,
                CAST(tiene_fotos AS BOOL) AS tiene_fotos,
                CAST(tiene_valoraciones AS BOOL) AS tiene_valoraciones,
                CAST(tiene_valoracion_media AS BOOL) AS tiene_valoracion_media,
                CAST(tiene_categoria_principal AS BOOL) AS tiene_categoria_principal,
                CAST(tiene_categorias_secundarias AS BOOL) AS tiene_categorias_secundarias,
                CAST(tiene_estado_operativo AS BOOL) AS tiene_estado_operativo,
                CAST(perfil_completitud AS FLOAT64) AS perfil_completitud,
                CAST(URL_valida_para_SEO AS BOOL) AS URL_valida_para_SEO,
                CAST(buena_valoracion AS BOOL) AS buena_valoracion,
                CAST(top5 AS BOOL) AS top5,
                CAST(n_fotos_max AS INT64) AS n_fotos_max,
                CAST(n_fotos_media AS INT64) AS n_fotos_media,
                CAST(n_reviews_max AS INT64) AS n_reviews_max,
                CAST(n_reviews_media AS INT64) AS n_reviews_media,
                categorias_no_incluidas,
                palabras_clave_en_resenas,
                CAST(orden_por_sentimiento AS INT64) AS orden_por_sentimiento,
                CAST(deberia_incluir_categoria_en_nombre AS BOOL) AS deberia_incluir_categoria_en_nombre,
                resenas_traducidas,
                palabras_clave,
                CAST(sentimiento_medio AS FLOAT64) AS sentimiento_medio,
                CAST(magnitud_sentimiento_media AS FLOAT64) AS magnitud_sentimiento_media,
                palabras_connotacion_positiva,
                palabras_connotacion_negativa,
                CAST(fuentes_consultadas AS INT64) AS fuentes_consultadas,
                CAST(fuentes_encontradas AS INT64) AS fuentes_encontradas,
                CAST(consistencia_nombre AS BOOL) AS consistencia_nombre,
                CAST(consistencia_localidad AS BOOL) AS consistencia_localidad,
                CAST(consistencia_provincia AS BOOL) AS consistencia_provincia,
                CAST(consistencia_direccion AS BOOL) AS consistencia_direccion,
                inconsistencias_directorios,
                fuentes_no_encontradas
            FROM `{self.client.project}.{dataset_id}.{source_table}`
            """

            self.client.query(query).result()
            print(f"Vista `{view_id}` creada correctamente.")
            return view_id
        except Exception as e:
            print(f"Error al crear la vista normalizada: {e}")
            return False
        
    def generate_query(self, dataset_id, source_table="Negocios"):
        """
        Crea o reemplaza una vista normalizada a partir de la tabla de negocios.
        Convierte campos potencialmente conflictivos como n_fotos_media y n_reviews_media.
        """
        try:
            query = f"""
            SELECT
                CAST(place_id AS STRING) AS place_id,
                CAST(main_business AS BOOL) AS main_business,
                CAST(nombre AS STRING) AS nombre,
                CAST(palabra_busqueda AS STRING) AS palabra_busqueda,
                CAST(direccion_completa AS STRING) AS direccion_completa,
                CAST(telefono_nacional AS STRING) AS telefono_nacional,
                CAST(telefono_internacional AS STRING) AS telefono_internacional,
                CAST(website AS STRING) AS website,
                CAST(n_fotos AS INT64) AS n_fotos,
                CAST(calle AS STRING) AS calle,
                CAST(ciudad AS STRING) AS ciudad,
                CAST(provincia AS STRING) AS provincia,
                CAST(codigo_postal AS STRING) AS codigo_postal,
                CAST(pais AS STRING) AS pais,
                CAST(valoracion_media AS FLOAT64) AS valoracion_media,
                CAST(n_valoraciones AS INT64) AS n_valoraciones,
                CAST(categoria_principal AS STRING) AS categoria_principal,
                CAST(categoria_principal_nombre AS STRING) AS categoria_principal_nombre,
                categorias_secundarias,
                CAST(estado_negocio AS STRING) AS estado_negocio,
                CAST(sin_local_fisico AS BOOL) AS sin_local_fisico,
                CAST(horario_normal AS BOOL) AS horario_normal,
                CAST(horario_festivo AS BOOL) AS horario_festivo,
                CAST(tiene_nombre AS BOOL) AS tiene_nombre,
                CAST(tiene_direccion AS BOOL) AS tiene_direccion,
                CAST(tiene_telefono AS BOOL) AS tiene_telefono,
                CAST(tiene_website AS BOOL) AS tiene_website,
                CAST(tiene_fotos AS BOOL) AS tiene_fotos,
                CAST(tiene_valoraciones AS BOOL) AS tiene_valoraciones,
                CAST(tiene_valoracion_media AS BOOL) AS tiene_valoracion_media,
                CAST(tiene_categoria_principal AS BOOL) AS tiene_categoria_principal,
                CAST(tiene_categorias_secundarias AS BOOL) AS tiene_categorias_secundarias,
                CAST(tiene_estado_operativo AS BOOL) AS tiene_estado_operativo,
                CAST(perfil_completitud AS FLOAT64) AS perfil_completitud,
                CAST(URL_valida_para_SEO AS BOOL) AS URL_valida_para_SEO,
                CAST(buena_valoracion AS BOOL) AS buena_valoracion,
                CAST(top5 AS BOOL) AS top5,
                CAST(n_fotos_max AS INT64) AS n_fotos_max,
                CAST(n_fotos_media AS INT64) AS n_fotos_media,
                CAST(n_reviews_max AS INT64) AS n_reviews_max,
                CAST(n_reviews_media AS INT64) AS n_reviews_media,
                categorias_no_incluidas,
                palabras_clave_en_resenas,
                CAST(deberia_incluir_categoria_en_nombre AS BOOL) AS deberia_incluir_categoria_en_nombre,
                resenas_traducidas,
                palabras_clave,
                CAST(sentimiento_medio AS FLOAT64) AS sentimiento_medio,
                CAST(magnitud_sentimiento_media AS FLOAT64) AS magnitud_sentimiento_media,
                palabras_connotacion_positiva,
                palabras_connotacion_negativa
            FROM `{self.client.project}.{dataset_id}.{source_table}`
            """
            #self.client.query(query).result()
            #print(f"Vista `{view_id}` creada correctamente.")
            return query
        except Exception as e:
            print(f"Error: {e}")
            return False

    # --- Helpers ---
    def _generate_dataset_id(self):
        """Genera un ID único para datasets."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"negocio_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def inferir_tipo(self, value):
        """Infiere el tipo de dato para BigQuery"""
        if value is None:
            return "STRING"  # BigQuery manejará la conversión a NULL
        if isinstance(value, bool):
            return "BOOL"
        elif isinstance(value, int):
            return "INT64" 
        elif isinstance(value, float):
            return "FLOAT64"     
        elif isinstance(value, list):
            return "ARRAY<STRING>"
        elif isinstance(value, str):
            return "STRING"
        # Default
        return "STRING"
    
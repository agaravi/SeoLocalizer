from google.cloud import bigquery

class Schemas:
    # Esquemas para cada posible tabla de BigQuery. 
    # Hay algunos campos eliminados que podrían servir para mayor profundidad del análisis en futuras versiones.
    SCHEMAS = {
        "Negocios": [
            bigquery.SchemaField("place_id", "STRING"),
            bigquery.SchemaField("main_business", "BOOLEAN"),
            bigquery.SchemaField("nombre", "STRING"),
            bigquery.SchemaField("palabra_busqueda", "STRING"),
            bigquery.SchemaField("direccion_completa", "STRING"),
            bigquery.SchemaField("telefono_nacional", "STRING"),
            bigquery.SchemaField("telefono_internacional", "STRING"),
            bigquery.SchemaField("website", "STRING"),
            bigquery.SchemaField("n_fotos", "INTEGER"),
            bigquery.SchemaField("calle", "STRING"),
            bigquery.SchemaField("ciudad", "STRING"),
            bigquery.SchemaField("provincia", "STRING"),
            bigquery.SchemaField("codigo_postal", "STRING"),
            bigquery.SchemaField("pais", "STRING"),
            bigquery.SchemaField("valoracion_media", "FLOAT"),
            bigquery.SchemaField("n_valoraciones", "INTEGER"),
            bigquery.SchemaField("categoria_principal", "STRING"),
            bigquery.SchemaField("categorias_secundarias", "STRING", mode="REPEATED"),
            bigquery.SchemaField("estado_negocio", "STRING"),
            bigquery.SchemaField("sin_local_fisico", "BOOLEAN"),
            bigquery.SchemaField("horario_normal", "BOOLEAN"),
            bigquery.SchemaField("horario_festivo", "BOOLEAN"),
            bigquery.SchemaField("tiene_nombre", "BOOLEAN"),
            bigquery.SchemaField("tiene_direccion", "BOOLEAN"),
            bigquery.SchemaField("tiene_telefono", "BOOLEAN"),
            bigquery.SchemaField("tiene_website", "BOOLEAN"),
            bigquery.SchemaField("tiene_fotos", "BOOLEAN"),
            bigquery.SchemaField("tiene_valoraciones", "BOOLEAN"),
            bigquery.SchemaField("tiene_valoracion_media", "BOOLEAN"),
            bigquery.SchemaField("tiene_categoria_principal", "BOOLEAN"),
            bigquery.SchemaField("tiene_categorias_secundarias", "BOOLEAN"),
            bigquery.SchemaField("tiene_estado_operativo", "BOOLEAN"),
            #bigquery.SchemaField("horario_regular", "STRING"),
            #bigquery.SchemaField("horario_secundario_regular", "STRING"),
            #bigquery.SchemaField("horario_actual", "STRING"),
            #bigquery.SchemaField("horario_actual_secundario", "STRING"),
            bigquery.SchemaField("perfil_completitud", "FLOAT"),
            #bigquery.SchemaField("resenas", "RECORD", mode="REPEATED", fields=[
            #    bigquery.SchemaField("autor", "STRING"),
            #    bigquery.SchemaField("texto", "STRING"),
            #    bigquery.SchemaField("fecha_publicacion", "STRING"),
            #    bigquery.SchemaField("fecha_relativa", "STRING"),
            #   bigquery.SchemaField("valoracion", "INTEGER")
            #]),
            bigquery.SchemaField("URL_valida_para_SEO", "BOOLEAN"),
            bigquery.SchemaField("buena_valoracion", "BOOLEAN"),
            bigquery.SchemaField("top5", "BOOLEAN"),
            #bigquery.SchemaField("n_fotos_max", "INTEGER"),
            bigquery.SchemaField("n_fotos_media", "INTEGER"),
            #bigquery.SchemaField("n_reviews_max", "INTEGER"),
            bigquery.SchemaField("n_reviews_media", "INTEGER"),
            bigquery.SchemaField("categorias_no_incluidas", "STRING", mode="REPEATED"),
            bigquery.SchemaField("palabras_clave_en_resenas", "STRING", mode="REPEATED"),
            bigquery.SchemaField("palabras_clave_en_resenas_competidores", "STRING", mode="REPEATED"),
            bigquery.SchemaField("deberia_incluir_categoria_en_nombre", "BOOLEAN"),
            bigquery.SchemaField("resenas_traducidas","STRING", mode="REPEATED"),
            bigquery.SchemaField("palabras_clave","RECORD", mode="REPEATED", fields=[
                bigquery.SchemaField("keyword", "STRING"),
                bigquery.SchemaField("indice_competicion", "INTEGER"),
                bigquery.SchemaField("busquedas_mensuales", "INTEGER")  
            ]),
            bigquery.SchemaField("sentimiento_medio", "FLOAT"),
            bigquery.SchemaField("magnitud_sentimiento_media", "FLOAT"),
            bigquery.SchemaField("palabras_connotacion_positiva", "STRING", mode="REPEATED"),
            bigquery.SchemaField("palabras_connotacion_negativa", "STRING", mode="REPEATED"),
            bigquery.SchemaField("orden_por_sentimiento", "INTEGER"),
            bigquery.SchemaField("fuentes_consultadas", "INTEGER"),
            bigquery.SchemaField("fuentes_encontradas", "INTEGER"),
            bigquery.SchemaField("consistencia_nombre", "BOOLEAN"),
            bigquery.SchemaField("consistencia_localidad", "BOOLEAN"),
            bigquery.SchemaField("consistencia_provincia", "BOOLEAN"),
            bigquery.SchemaField("consistencia_direccion", "BOOLEAN"),
            bigquery.SchemaField("inconsistencias_directorios", "STRING", mode="REPEATED"),
            bigquery.SchemaField("fuentes_no_encontradas", "STRING", mode="REPEATED"),
        ]
    }

    @classmethod
    def get_table_schema(self, table_name):
        """Obtiene el esquema para una tabla específica"""
        return self.SCHEMAS.get(table_name, [])
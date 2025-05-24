from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

@dataclass
class BusinessReview: # No se almacenan en bigquery
    """
    Modelo para representar reseñas de negocios.
    Campos todos opcionales para manejar datos parciales.
    """
    autor: Optional[str] = None
    texto: Optional[str] = None
    valoracion: Optional[int] = None
    fecha_publicacion: Optional[str] = None  # ISO format string
    fecha_publicacion_relativa: Optional[str] = None

    def get_year_fecha_publicacion(self):
        "Funcion para obtener el año de publicación de la review"
        date = datetime.fromisoformat(self.fecha_publicacion.replace("Z", ""))  # Quitar la 'Z' al final
        year = date.year

        return year

    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "autor": self.autor,
            "texto": self.texto,
            "valoracion": int(self.valoracion) if self.valoracion is not None else None,
            "fecha_publicacion": self.fecha_publicacion,
            "fecha_relativa": self.fecha_publicacion_relativa
        }

@dataclass
class BusinessAddress:
    """
    Modelo para direcciones postales estructuradas.
    """
    calle: Optional[str] = None
    ciudad: Optional[str] = None
    provincia: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = None
    pais_code: Optional[str] = None  # Ej: "ES" para España
    direccion_completa: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "calle": self.calle,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "codigo_postal": self.codigo_postal,
            "pais": self.pais,
            "pais_code": self.pais_code,
            "direccion_completa": self.direccion_completa
        }

@dataclass
class BusinessHours: # EN DESUSO
    """
    Modelo para horarios de negocio.
    """
    regular: Optional[Dict[str, Any]] = None
    actual: Optional[Dict[str, Any]] = None
    secundario_regular: Optional[Dict[str, Any]] = None
    secundario_actual: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "regular": self.regular,
            "actual": self.actual,
            "secundario_regular": self.secundario_regular,
            "secundario_actual": self.secundario_actual
        }
    
@dataclass
class BusinessKeywordSuggestions:
    """
    Modelo para sugerencias de keywords.
    """
    keyword: Optional[str] = None
    indice_competicion: Optional[int] = None
    busquedas_mensuales: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyword": self.keyword,
            "indice_competicion": self.indice_competicion,
            "busquedas_mensuales": self.busquedas_mensuales
        }

@dataclass
class Business:
    """
    Modelo principal para representar un negocio.
    Campos obligatorios: place_id y main_business.
    El resto son opcionales.
    """
    place_id: str  # Requerido
    main_business: bool # Requerido
    palabra_busqueda: str # Requerido
    nombre: Optional[str] = None  

    
    # Información básica
    direccion: Optional[BusinessAddress] = None
    telefono_nacional: Optional[str] = None
    telefono_internacional: Optional[str] = None
    website: Optional[str] = None
    categoria_principal: Optional[str] = None
    categoria_principal_nombre: Optional[str] = None
    categorias_secundarias: List[str] = field(default_factory=list)
    n_fotos: Optional[int] = None


    # Grado de completitud del negocio
    tiene_nombre: Optional[bool] = None
    tiene_direccion: Optional[bool] = None
    tiene_telefono: Optional[bool] = None
    tiene_website: Optional[bool] = None
    tiene_fotos: Optional[bool] = None
    tiene_valoraciones: Optional[bool] = None
    tiene_valoracion_media: Optional[bool] = None
    tiene_categoria_principal: Optional[bool] = None
    tiene_categorias_secundarias: Optional[bool] = None
    tiene_estado_operativo: Optional[bool] = None
    
    # Reputación
    valoracion_media: Optional[float] = None
    n_valoraciones: Optional[int] = None
    
    # Estado operativo
    estado_negocio: Optional[str] = None
    sin_local_fisico: Optional[bool] = None

        
    # Horarios
    horario: Optional[BusinessHours] = None
    horario_normal: Optional[bool] = None # Sirve para el grado de completitud del negocio
    horario_festivo: Optional[bool] = None # Sirve para el grado de completitud del negocio
    
    # Reseñas
    reviews: List[BusinessReview] = field(default_factory=list)
    reviews_traducidas: Optional[List[str]]= field(default_factory=list)

    # Campos añadidos sobre las comparaciones
    URL_valida_para_SEO:Optional[bool] = None
    buena_valoracion: Optional[bool] = None # Una valoración superior a 4 estrellas
    top5:Optional[bool] = None
    n_fotos_max:Optional[int] = None
    n_fotos_media:Optional[int] = None
    n_reviews_max:Optional[int] = None
    n_reviews_media:Optional[int] = None
    categorias_no_incluidas:Optional[List[str]] = field(default_factory=list)  # O también dicho "palabras clave no incluidas"
    deberia_incluir_categoria_en_nombre:Optional[bool] = None
    palabras_clave_en_resenas:Optional[List[str]] = field(default_factory=list) 
    palabras_clave_en_resenas_competidores:Optional[List[str]] = field(default_factory=list)  #esto es basicamente categorias no incluidas

    # Campos añadidos sobre palabras clave
    palabras_clave: List[BusinessKeywordSuggestions] = field(default_factory=list)

    # Campos añadidos sobre analisis de sentimiento
    sentimiento_medio: Optional[float] = None
    magnitud_sentimiento_media: Optional[float] = None
    palabras_connotacion_positiva: Optional[List[str]] = field(default_factory=list) 
    palabras_connotacion_negativa: Optional[List[str]] = field(default_factory=list) 
    orden_por_sentimiento: Optional[List[str]] = field(default_factory=list)

    # Campos añadidos sobre citaciones locales
    fuentes_consultadas:Optional[int] = None
    fuentes_encontradas:Optional[int] = None
    consistencia_nombre:Optional[bool] = None
    consistencia_localidad:Optional[bool] = None
    consistencia_provincia:Optional[bool] = None
    consistencia_direccion:Optional[bool] = None
    inconsistencias_directorios:Optional[List[str]] = field(default_factory=list)
    fuentes_no_encontradas:Optional[List[str]] = field(default_factory=list) 
 
    
    
    # Métodos de negocio
    def calculate_completeness(self) -> float:
        """Calcula el porcentaje de completitud del perfil (0-100)."""
        completeness=0
        fields = {
            "tiene_nombre": self.tiene_nombre,
            "tiene_direccion": self.tiene_direccion,
            "tiene_telefono": self.tiene_telefono,
            "tiene_fotos":self.tiene_fotos,
            "tiene_website": self.tiene_website,
            "tiene_horario_normal":self.horario_normal,
            "tiene_horario_festivo":self.horario_festivo,
            "tiene_categoria_principal": self.tiene_categoria_principal,
            "tiene_categorias_secundarias": self.tiene_categorias_secundarias,
            "tiene_valoraciones": self.tiene_valoraciones,
            "tiene_valoracion_media": self.tiene_valoracion_media,
            "tiene_estado_operativo": self.tiene_estado_operativo,
        }
        for key,value in fields.items():
            if key=="tiene_horario_festivo" and value==True:
                completeness+=0.5
            elif value==True:
                completeness+=1

        #print(completeness)
        #print((completeness/12)*100)

        return ((completeness/11.5)*100)
    
    def validate_fields_and_completeness(self):
        redes_sociales = [
            "facebook.com", "instagram.com", "twitter.com", "tiktok.com",
            "linkedin.com", "youtube.com", "pinterest.com"
        ]  
        self.URL_valida_para_SEO=True
        self.tiene_website=self.has_website()
        if self.tiene_website==True:
            for red in redes_sociales:
                if red in self.website.lower():
                    self.URL_valida_para_SEO = False
                    break
        else:
            self.URL_valida_para_SEO = False

        self.tiene_nombre=self.has_name()
        self.tiene_direccion=self.has_address()
        self.tiene_telefono=self.has_phone()
        self.tiene_fotos=self.has_photos()
        self.tiene_valoraciones=self.has_reviews()
        self.tiene_valoracion_media=self.has_review_score()
        if self.tiene_valoracion_media==True:
            self.buena_valoracion=bool(self.valoracion_media>4)
        self.tiene_categoria_principal=self.has_main_category()
        self.tiene_categorias_secundarias=self.has_secondary_categories()
        self.tiene_estado_operativo=self.has_operational_state()
        #print(URL_valida_para_SEO)

    def has_name(self) ->bool:
        return bool(self.nombre)
    
    def has_address(self) -> bool:
        return bool(self.direccion.direccion_completa)
    
    def has_photos(self) ->bool:
        return bool(self.n_fotos)

    def has_website(self) -> bool:
        return bool(self.website)

    def has_phone(self) -> bool:
        return bool(self.telefono_nacional) or bool(self.telefono_internacional)

    def has_reviews(self) ->bool:
        return bool(self.n_valoraciones) and self.n_valoraciones>0

    def has_review_score(self) ->bool:
        return bool(self.valoracion_media) and self.valoracion_media>0
    
    def has_main_category(self) -> bool:
        return bool(self.categoria_principal) or bool(self.categoria_principal_nombre)
    
    def has_secondary_categories(self) -> bool:
        return bool(self.categorias_secundarias) and self.categorias_secundarias!=[]
    
    def has_operational_state(self) -> bool:
        return bool(self.estado_negocio) and self.estado_negocio=="OPERATIONAL"  
    
    # GETTERS    
    def get_reviews(self):
        reviews=[]
        if self.n_valoraciones!= 0:
            for review in self.reviews:
                if review.texto is not None:
                    reviews.append(review)
        return reviews
    
    def get_translated_reviews(self):
        if self.reviews_traducidas!=[]:
            return self.reviews_traducidas
 
    # SETTERS
    #@classmethod
    def set_from_google_places(self, place_data):
        """Constructor desde API de Google Places."""
        direccion = place_data.get('postalAddress', {})

        reviews = [
            BusinessReview(
                autor=review.get('authorAttribution', {}).get('displayName'),
                texto=review.get('originalText', {}).get('text'),
                valoracion=review.get('rating'),
                fecha_publicacion=review.get('publishTime'),
                fecha_publicacion_relativa=review.get('relativePublishTimeDescription')
            ) for review in place_data.get('reviews', [])
        ]
        
        self.nombre=place_data.get('displayName', {}).get('text', '')
        self.direccion=BusinessAddress(
                calle=', '.join(direccion.get('addressLines', [])),
                ciudad=direccion.get('locality'),
                provincia=direccion.get('administrativeArea'),
                codigo_postal=direccion.get('postalCode'),
                pais_code=direccion.get('regionCode'),
                direccion_completa=place_data.get('formattedAddress')
            )
        self.telefono_nacional=place_data.get('nationalPhoneNumber')
        self.telefono_internacional=place_data.get('internationalPhoneNumber')
        self.website=place_data.get('websiteUri')
        self.categoria_principal=place_data.get('primaryType')
        self.categoria_principal_nombre=place_data.get('primaryTypeDisplayName')
        self.categorias_secundarias=place_data.get('types', [])
        self.valoracion_media=place_data.get('rating')
        self.n_valoraciones=place_data.get('userRatingCount')
        self.estado_negocio=place_data.get('businessStatus')
        self.sin_local_fisico=place_data.get('pureServiceAreaBusiness')
        self.n_fotos=len(place_data.get("photos",[]))
        self.horario_normal=bool(place_data.get('regularOpeningHours')) or bool(place_data.get('currentOpeningHours'))
        self.horario_festivo= bool(place_data.get('regularSecondaryOpeningHours')) or bool(place_data.get('currentSecondaryOpeningHours'))
        """self.horario=BusinessHours(
                regular=place_data.get('regularOpeningHours'),
                actual=place_data.get('currentOpeningHours'),
                secundario_regular=place_data.get('regularSecondaryOpeningHours'),
                secundario_actual=place_data.get('currentSecondaryOpeningHours')
            )"""
        self.reviews=reviews
    
    #@classmethod
    def set_comparison_data(self,comparison_data):
        self.top5=comparison_data["top5"]
        self.n_fotos_max=comparison_data["n_fotos_max"]
        self.n_fotos_media=comparison_data["n_fotos_media"]
        self.n_reviews_max=comparison_data["n_reviews_max"]
        self.n_reviews_media=comparison_data["n_reviews_media"]
        self.categorias_no_incluidas=comparison_data["categorias_no_incluidas"]
        self.palabras_clave_en_resenas=comparison_data["keywords_in_reviews"]
        self.palabras_clave_en_resenas_competidores=comparison_data["keywords_in_reviews_competitors"]
        self.deberia_incluir_categoria_en_nombre=comparison_data["should_include_category_in_name"]

    def set_keyword_suggestions(self,keywords_info):
        self.palabras_clave=[]
        for word in keywords_info:
            self.palabras_clave.append(
                BusinessKeywordSuggestions(
                    keyword=word["keyword"],
                    indice_competicion=word["indice_competicion"],
                    busquedas_mensuales=word["busquedas_mensuales"]
                )
        )
    def set_reviews_translation(self,reviews_traduction):
        self.reviews_traducidas=reviews_traduction

    def set_categories_translation(self,main_category,secondary_categories):
        self.categoria_principal=main_category
        self.categorias_secundarias=secondary_categories
        #self.categorias_no_incluidas=categorias_no_incluidas
        #self.palabras_clave_en_resenas=palabras_clave_en_resenas,
        #self.palabras_clave_en_resenas_competidores=palabras_clave_en_resenas_competidores

    def set_sentiment_analysis(self, sentiment_analysis_results, top_positive_words, top_negative_words, entities_mentioned):
        """ Asigna los resultados del análisis de sentimiento al objeto Business. """
        self.sentimiento_medio=sentiment_analysis_results["average_score"]
        self.magnitud_sentimiento_media=sentiment_analysis_results["average_magnitude"]
        if top_positive_words is not None:
            self.palabras_connotacion_positiva=[word for word, _ in top_positive_words]
        if top_negative_words is not None:
            self.palabras_connotacion_negativa=[word for word, _ in top_negative_words]
        if self.main_business==True and entities_mentioned is not None:
            self.palabras_clave_en_resenas.extend(entities_mentioned)       

    def set_sentiment_order(self, sentiment_order):
        for item in sentiment_order:
            for business_name, rank in item.items():
                if business_name==self.nombre:
                    self.orden_por_sentimiento=rank
    

    def set_citacions_data(self,citation_data):
        self.fuentes_consultadas=citation_data["consulted_sources"]
        self.fuentes_encontradas=citation_data["found_sources"]
        self.consistencia_nombre=citation_data["name_consistency"]
        self.consistencia_localidad=citation_data["locality_consistency"]
        self.consistencia_provincia=citation_data["province_consistency"]
        self.consistencia_direccion=citation_data["address_consistency"]
        self.inconsistencias_directorios=citation_data["directory_inconsistences"]
        self.fuentes_no_encontradas=citation_data["not_found_sources"]
            
    # SERIALIZACIÓN PARA BIGQUERY
    """def to_dict(self) -> Dict[str, Any]:
        Convierte el objeto a diccionario para BigQuery/JSON.
        data = {
            "place_id": self.place_id,
            "nombre": self.nombre,
            "main_business":self.main_business,
            "direccion": self.direccion.to_dict() if self.direccion else None,
            "telefono_nacional": self.telefono_nacional,
            "telefono_internacional": self.telefono_internacional,
            "website": self.website,
            "n_fotos": self.n_fotos,
            "categoria_principal": self.categoria_principal,
            "categoria_principal_nombre": self.categoria_principal_nombre,
            "categorias_secundarias": self.categorias_secundarias,
            "valoracion_media": self.valoracion_media,
            "n_valoraciones": self.n_valoraciones,
            "estado_negocio": self.estado_negocio,
            "sin_local_fisico": self.sin_local_fisico ,
            "horario": self.horario.to_dict() if self.horario else None,
            "reviews": [review.to_dict() for review in self.reviews],
            "perfil_completitud": self.calculate_completeness(),
            "URL_valida_para_SEO": self.URL_valida_para_SEO,
            "top5": self.top5 ,
            "n_fotos_max": self.n_fotos_max ,
            "n_fotos_media": self.n_fotos_media,
            "n_reviews_max": self.n_reviews_max,
            "n_reviews_media": self.n_reviews_media,
            "categorias_no_incluidas": self.categorias_no_incluidas,
            "deberia_incluir_categoria_en_nombre": self.deberia_incluir_categoria_en_nombre,
            "palabras_clave":[palabra.to_dict() for palabra in self.palabras_clave]
        }       
        return data
    
    def to_bigquery_format(self) -> Dict[str, Any]:
        
        Generates a dictionary strictly matching the 'Negocios' table schema in schemas.py
        for use with the upsert_business function.
               
        data = self.to_dict()
        bq_row = {}

        # Direct mapping or default values
        bq_row["place_id"] = data.get("place_id")
        bq_row["main_business"] = data.get("main_business", False) # Default for BOOLEAN
        bq_row["nombre"] = data.get("nombre")
        bq_row["telefono_nacional"] = data.get("telefono_nacional")
        bq_row["telefono_internacional"] = data.get("telefono_internacional")
        bq_row["website"] = data.get("website")
        bq_row["n_fotos"] = data.get("n_fotos")
        bq_row["valoracion_media"] = data.get("valoracion_media")
        bq_row["n_valoraciones"] = data.get("n_valoraciones")
        bq_row["categoria_principal"] = data.get("categoria_principal")
        bq_row["categoria_principal_nombre"] = data.get("categoria_principal_nombre")
        bq_row["categorias_secundarias"] = data.get("categorias_secundarias", [])
        bq_row["estado_negocio"] = data.get("estado_negocio")
        bq_row["sin_local_fisico"] = data.get("sin_local_fisico", False) # Default for BOOLEAN
        bq_row["perfil_completitud"] = data.get("perfil_completitud")
        bq_row["URL_valida_para_SEO"] = data.get("URL_valida_para_SEO", False) # Default for BOOLEAN
        bq_row["top5"] = data.get("top5", False) # Default for BOOLEAN
        bq_row["n_fotos_max"] = data.get("n_fotos_max")
        bq_row["n_fotos_media"] = data.get("n_fotos_media")
        bq_row["n_reviews_max"] = data.get("n_reviews_max")
        bq_row["n_reviews_media"] = data.get("n_reviews_media")
        bq_row["categorias_no_incluidas"] = data.get("categorias_no_incluidas", [])
        bq_row["deberia_incluir_categoria_en_nombre"] = data.get("deberia_incluir_categoria_en_nombre", False) # Default
        bq_row["resenas_traducidas"] = data.get("resenas_traducidas", [])

        # Address fields (flattened from direccion_details)
        address_details = data.get("direccion_details")
        if address_details:
            bq_row["direccion_completa"] = address_details.get("direccion_completa")
            bq_row["calle"] = address_details.get("calle") 
            bq_row["ciudad"] = address_details.get("ciudad")
            bq_row["provincia"] = address_details.get("provincia")
            bq_row["codigo_postal"] = address_details.get("codigo_postal")
            bq_row["pais"] = address_details.get("pais")
        else:
            for addr_field in ["direccion_completa", "calle", "ciudad", "provincia", "codigo_postal", "pais"]:
                bq_row[addr_field] = None
        
        # Horario fields (JSON strings from horario_details)
        horario_details = data.get("horario_details")
        if horario_details:
            bq_row["horario_regular"] = json.dumps(horario_details.get("regular")) if horario_details.get("regular") is not None else None
            bq_row["horario_secundario_regular"] = json.dumps(horario_details.get("secundario_regular")) if horario_details.get("secundario_regular") is not None else None
            bq_row["horario_actual"] = json.dumps(horario_details.get("actual")) if horario_details.get("actual") is not None else None
            # Mapping model's 'secundario_actual' to schema's 'horario_actual_secundario'
            bq_row["horario_actual_secundario"] = json.dumps(horario_details.get("secundario_actual")) if horario_details.get("secundario_actual") is not None else None
        else:
            for hour_field in ["horario_regular", "horario_secundario_regular", "horario_actual", "horario_actual_secundario"]:
                bq_row[hour_field] = None
                
        # Reviews (reseñas) - should be correctly formatted by BusinessReview.to_dict()
        bq_row["resenas"] = data.get("reviews_list", [])

        # If 'palabras_clave' were added to schema as, for example, 'palabras_clave_record' (REPEATED RECORD)
        # you would add:
        bq_row["palabras_clave"] = data.get("palabras_clave_list", [])
        
        return {k: v for k, v in bq_row.items() if v is not None}

        return bq_row"""
    def to_bigquery_format(self) -> Dict[str, Any]:
        """Versión optimizada que coincide exactamente con tu esquema"""
        data = {
            # Campos exactamente como en SCHEMAS
            "place_id": self.place_id,
            "main_business": self.main_business,
            "nombre": self.nombre,
            "palabra_busqueda": self.palabra_busqueda,
            "direccion_completa": self.direccion.direccion_completa if self.direccion else None,
            "telefono_nacional": self.telefono_nacional,
            "telefono_internacional": self.telefono_internacional,
            "website": self.website,
            "n_fotos": self.n_fotos,
            "calle": self.direccion.calle if self.direccion else None,
            "ciudad": self.direccion.ciudad if self.direccion else None,
            "provincia": self.direccion.provincia if self.direccion else None,
            "codigo_postal": self.direccion.codigo_postal if self.direccion else None,
            "pais": self.direccion.pais if self.direccion else None,
            "valoracion_media": self.valoracion_media,
            "n_valoraciones": self.n_valoraciones,
            "categoria_principal": self.categoria_principal,
            "categoria_principal_nombre": self.categoria_principal_nombre,
            "categorias_secundarias": self.categorias_secundarias,
            "estado_negocio": self.estado_negocio,
            "sin_local_fisico": self.sin_local_fisico,  # Permite NULL como necesitas
            "horario_normal": self.horario_normal,
            "horario_festivo": self.horario_festivo,
            #"horario_regular": json.dumps(self.horario.regular) if self.horario and self.horario.regular else None,
            #"horario_secundario_regular": json.dumps(self.horario.secundario_regular) if self.horario and self.horario.secundario_regular else None,
            #"horario_actual": json.dumps(self.horario.actual) if self.horario and self.horario.actual else None,
            #"horario_actual_secundario": json.dumps(self.horario.secundario_actual) if self.horario and self.horario.secundario_actual else None,
            "perfil_completitud": self.calculate_completeness() if self.main_business==True else None,
            "tiene_nombre": self.tiene_nombre,
            "tiene_direccion": self.tiene_direccion,
            "tiene_telefono": self.tiene_telefono,
            "tiene_fotos":self.tiene_fotos,
            "tiene_website": self.tiene_website,
            "tiene_categoria_principal": self.tiene_categoria_principal,
            "tiene_categorias_secundarias": self.tiene_categorias_secundarias,
            "tiene_valoraciones": self.tiene_valoraciones,
            "tiene_valoracion_media": self.tiene_valoracion_media,
            "tiene_estado_operativo": self.tiene_estado_operativo,
            #"resenas": [{
            #    "autor": r.autor,
            #    "texto": r.texto,
            #    "fecha_publicacion": r.fecha_publicacion,
            #   "fecha_relativa": r.fecha_publicacion_relativa,
            #    "valoracion": r.valoracion
            #} for r in self.reviews],
            "URL_valida_para_SEO": self.URL_valida_para_SEO,
            "buena_valoracion": self.buena_valoracion,
            "top5": self.top5,
            "n_fotos_max": self.n_fotos_max,
            "n_fotos_media": self.n_fotos_media,
            "n_reviews_max": self.n_reviews_max,
            "n_reviews_media": self.n_reviews_media,
            "categorias_no_incluidas": self.categorias_no_incluidas if self.main_business==True else None,
            "deberia_incluir_categoria_en_nombre": self.deberia_incluir_categoria_en_nombre,
            "palabras_clave_en_resenas": self.palabras_clave_en_resenas,
            "resenas_traducidas": self.reviews_traducidas,
            "palabras_clave": [{
                "keyword": p.keyword,
                "indice_competicion": p.indice_competicion,
                "busquedas_mensuales": p.busquedas_mensuales
            } for p in self.palabras_clave] if self.palabras_clave!=[] else None,
            "sentimiento_medio":self.sentimiento_medio,
            "magnitud_sentimiento_media":self.magnitud_sentimiento_media,
            "palabras_connotacion_positiva": self.palabras_connotacion_positiva,
            "palabras_connotacion_negativa": self.palabras_connotacion_negativa,
            "orden_por_sentimiento":self.orden_por_sentimiento,
            "fuentes_consultadas":self.fuentes_consultadas,
            "fuentes_encontradas":self.fuentes_encontradas,
            "consistencia_nombre": self.consistencia_nombre,
            "consistencia_localidad": self.consistencia_localidad,
            "consistencia_provincia":self.consistencia_provincia,
            "consistencia_direccion":self.consistencia_direccion,
            "inconsistencias_directorios":self.inconsistencias_directorios,
            "fuentes_no_encontradas":self.fuentes_no_encontradas,
        }
        
        # Filtramos None pero mantenemos False/0/""
        return {k: v for k, v in data.items() if v is not None}
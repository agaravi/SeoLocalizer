import unidecode
import os
from google.ads.googleads.client import GoogleAdsClient
"""Script para generar ideas de palabras clave para SEO."""
"""Basado en el script oficial de Google Ads """

# --- INICIO DEL CÓDIGO REFERENCIADO / ADAPTADO ---
# Este código ha sido adaptado del ejemplo oficial de Google Ads API para Python.
# Fuente original: https://github.com/googleads/google-ads-python/blob/main/examples/planning/generate_keyword_ideas.py
# Copyright 2019 Google LLC
# Licencia: Apache License, Version 2.0
# Se han realizado modificaciones para integrar la funcionalidad en el proyecto SEOLocalizer,
# incluyendo la adición de lógica de filtrado y la adaptación a las clases de modelo del proyecto.
# --- FIN DEL CÓDIGO REFERENCIADO / ADAPTADO ---


LOGIN_CUSTOMER_ID = os.environ.get("LOGIN_CUSTOMER_ID")

def get_keyword_ideas(client,categoria,ciudad):

    # Cargar cliente de Google Ads
    #client=GoogleAdsClient()
    
    categorias=[categoria,categoria+" "+ciudad]

    # 1. Accede al servicio
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    
    # 2. Prepara la solicitud
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = LOGIN_CUSTOMER_ID
    request.language = "languageConstants/1003"
    request.keyword_seed.keywords.extend(categorias)
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
    request.keyword_annotation.extend([
        client.enums.KeywordPlanKeywordAnnotationEnum.KEYWORD_CONCEPT
    ])

    # 3. Ejecutar
    response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
    ideas=[]
    for idea in response:
        if idea.text.lower() in [x.lower() for x in categorias]:
           continue
        if "gratis" in idea.text.lower():
            continue
        conceptos = idea.keyword_annotations.concepts
        conceptos_a_excluir=["Otras Marcas", "Marcas", "Color", "BRAND", "Detallista", "Mujer","Cadena","Hombre","Plato"]
        
        # Si alguno de los conceptos está en la lista de exclusión, salta
        if any(
            c.name.lower() in [x.lower() for x in conceptos_a_excluir] or
            c.concept_group.name.lower() in [x.lower() for x in conceptos_a_excluir] or
            c.concept_group.type_ in conceptos_a_excluir or
            ((c.concept_group.type_=="Ciudad" or c.concept_group.name=="Ciudad") and unidecode.unidecode(c.name.lower())!=unidecode.unidecode(ciudad).lower()) #si encuentra la ciudad, tiene que coincidir con la dada
            for c in conceptos
        ):
            continue

        if idea.keyword_idea_metrics.competition_index<=60 and idea.keyword_idea_metrics.competition_index>=2 and idea.keyword_idea_metrics.avg_monthly_searches>=20:
            ideas.append({"keyword": idea.text, "indice_competicion" : idea.keyword_idea_metrics.competition_index, "busquedas_mensuales": idea.keyword_idea_metrics.avg_monthly_searches,
                          "concepts": idea.keyword_annotations.concepts})
            print(idea.text)
        if len(ideas) >= 10:
            break  # Detiene el for cuando ya hay 10 ideas
    
    print(ideas)
    return ideas
    

#get_keyword_ideas("taller de coches", "Córdoba")
from pathlib import Path
import unidecode


from google.ads.googleads.client import GoogleAdsClient

# Ejemplo: Extraer palabras clave
def get_keyword_ideas(client,categoria,ciudad):

    # Cargar cliente de Google Ads
    #client=GoogleAdsClient()
    
    categorias=[categoria,categoria+" "+ciudad]

    # 1. Accede al servicio
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
    
    # 2. Prepara la solicitud
    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = "3035650339"  # Ej: "1234567890"
    request.language = "languageConstants/1003"
    request.keyword_seed.keywords.extend(categorias)
    request.keyword_plan_network = client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
    request.keyword_annotation.extend([
        client.enums.KeywordPlanKeywordAnnotationEnum.KEYWORD_CONCEPT
    ])

    
    # 3. Ejecutar
    response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
    #print(response)
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
            ((c.concept_group.type_=="Ciudad" or c.concept_group.name=="Ciudad") and unidecode.unidecode(c.concept_group.name.lower())!=unidecode.unidecode(ciudad)) #si encuentra la ciudad, tiene que coincidir con la dada
            for c in conceptos
        ):
            continue

        if idea.keyword_idea_metrics.competition_index<=60 and idea.keyword_idea_metrics.competition_index>=2 and idea.keyword_idea_metrics.avg_monthly_searches>=20:
            ideas.append({"keyword": idea.text, "indice_competicion" : idea.keyword_idea_metrics.competition_index, "busquedas_mensuales": idea.keyword_idea_metrics.avg_monthly_searches,
                          "concepts": idea.keyword_annotations.concepts})
            print(idea.text)
        if len(ideas) >= 10:
            break  # Detiene el for cuando ya hay 10 ideas
        #print(idea.text)
    
    print(ideas)
    return ideas
    #print(ideas["keyword"])
    

#get_keyword_ideas("taller de coches", "Córdoba")
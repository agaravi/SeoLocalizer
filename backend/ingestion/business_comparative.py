from typing import List
import statistics
from backend.business.models import Business
#from processing.traduction import *
from backend.processing.google_traduction import *


def compare_business(main_business:Business,competitors:List[Business]):
    top5=False
    categorias_no_incluidas = []
    should_include_category_in_name = False
    all_photos = []
    all_reviews = []
    all_categories =[]
    competitor_categories = []
    keywords_in_reviews_competitors = []
    keywords_in_reviews = []

    main_business_name=main_business.nombre


    # Comparar categorías
    main_business_categories = []
    #translate_keywords(main_business)
    #translate_keywords_google(main_business)
    if main_business.categoria_principal:
        main_business_categories.append(main_business.categoria_principal)
    if main_business.categorias_secundarias:
        main_business_categories.extend(main_business.categorias_secundarias)

    all_categories.extend(main_business_categories)

    for comp in competitors:
        #print(name)
        if main_business_name==comp.nombre:
           top5=True
        
        if hasattr(comp, 'n_fotos') and comp.n_fotos is not None:
            all_photos.append(comp.n_fotos)
        
        if hasattr(comp, 'n_valoraciones') and comp.n_valoraciones is not None:
            all_reviews.append(comp.n_valoraciones)
        
        #translate_keywords(comp)
        #translate_keywords_google(comp)
        if comp.categoria_principal:
            competitor_categories.append(comp.categoria_principal)
        if comp.categorias_secundarias:
            competitor_categories.extend(comp.categorias_secundarias)

        all_categories.extend(competitor_categories)

        # Verificar inclusión de categoría en nombre
        if comp.nombre == main_business_name:
            continue  # Saltar si es el mismo negocio
        for cat in competitor_categories:
            if isinstance(cat, list):
                for subcat in cat:
                    #cleaned_subcat=translate(subcat)
                    print(subcat.lower())
                    print(comp.nombre.lower())
                    if subcat.lower() in comp.nombre.lower():      
                        # Si al menos una categoría aparece en su nombre, y no aparece en el nuestro
                        if not any(subcat.lower() in main_business_name.lower() for subcat in main_business_categories):
                            should_include_category_in_name = True
                            break
                    if subcat not in main_business_categories:
                        print(subcat)
                        categorias_no_incluidas.append(subcat)
            elif isinstance(cat, str):
                #if cat==None:
                #   break
                #cleaned_cat=translate(cat)
                print(cat.lower())
                print(comp.nombre.lower())
                if cat not in main_business_categories:
                    print(cat)
                    categorias_no_incluidas.append(cat)
                if cat.lower() in comp.nombre.lower():
                    if not any(cat.lower() in main_business_name.lower() for cat in main_business_categories):
                        should_include_category_in_name = True
                        break

       # for category in competitor_categories:
            #if cat and cat not in main_business_categories:
                #print(cat)
                #categorias_no_incluidas.extend(cat)

    all_categories=list(set(all_categories)) # Eliminar duplicados

    # Verificar inclusión de palabras clave en las reseñas del negocio principal
    main_business_reviews=main_business.get_translated_reviews()
    if main_business_reviews:
        for review in main_business_reviews:
            for keyword in all_categories:
                print(keyword)
                if keyword in review:
                    print("la encontré en la review")
                    keywords_in_reviews.append(keyword)
    
    # Verificar inclusión de palabras clave en las reseñas de los competidores
    competitor_reviews=comp.get_translated_reviews()
    excluded_categories = [category for category in all_categories if category not in keywords_in_reviews]
    if competitor_reviews:
        for review in competitor_reviews:
            for keyword in excluded_categories:
                print(keyword)
                if keyword in review:
                    print("la encontré en la review")
                    keywords_in_reviews_competitors.append(keyword)
        

    if main_business.n_fotos is not None:
        all_photos.append(main_business.n_fotos)
    
    if main_business.n_valoraciones is not None:
        all_reviews.append(main_business.n_valoraciones)
    
    # Cálculo de estadísticas (con manejo de listas vacías)
    n_fotos_max = max(all_photos) if all_photos else 0
    n_fotos_media = int(round(statistics.mean(all_photos))) if all_photos else 0
    n_reviews_max = max(all_reviews) if all_reviews else 0
    n_reviews_media = int(round(statistics.mean(all_reviews))) if all_reviews else 0

    if keywords_in_reviews_competitors:
        main_business.categorias_no_incluidas.extend(keywords_in_reviews_competitors)
   
    return {
        "top5": top5,
        "n_fotos_max": n_fotos_max,
        "n_fotos_media": n_fotos_media,
        "n_reviews_max": n_reviews_max,
        "n_reviews_media": n_reviews_media,
        "categorias_no_incluidas": list(categorias_no_incluidas),
        "should_include_category_in_name": should_include_category_in_name,
        "keywords_in_reviews": list(set(keywords_in_reviews)),
        "keywords_in_reviews_competitors": list(set(keywords_in_reviews_competitors))
    }

"""

    # Obtener categorías de competidores
    competitor_categorias_principales = bigquery_client.select_one_field_from_business(table_dataset_ids, "categoria_principal", False)
    competitor_categorias_secundarias = bigquery_client.select_one_field_from_business(table_dataset_ids, "categorias_secundarias", False)
    #print(competitor_categorias_principales)
    #print(competitor_categorias_secundarias)
    competitor_categories = set([competitor_categorias_principales[0]["categoria_principal"]] + competitor_categorias_secundarias[0]["categorias_secundarias"])

    # Comparar categorías
    for category in competitor_categories:
        if category and category not in main_business_categories:
            categorias_no_incluidas.add(category)

    # Analizar si alguno de los top5 (que no sea el main) tiene la categoría en su nombre
    for comp_name in competitor_names[0]:
        if comp_name == main_business_name:
            continue  # Saltar si es el mismo negocio
        for cat in competitor_categories:
            if isinstance(cat, list):
                for subcat in cat:
                    if subcat.lower() in comp_name.lower():
                        # Si al menos una categoría aparece en su nombre, y no aparece en el nuestro
                        if not any(subcat.lower() in main_business_name.lower() for subcat in main_business_categories):
                            should_include_category_in_name = True
                            break
            elif isinstance(cat, str):
                if cat.lower() in comp_name.lower():
                    if not any(cat.lower() in main_business_name.lower() for cat in main_business_categories):
                        should_include_category_in_name = True
                        break

    resultado={
        "top5": top5,
        "n_fotos_max": n_fotos_max,
        "n_fotos_media": n_fotos_media,
        "n_reviews_max": n_reviews_max,
        "n_reviews_media": n_reviews_media,
        "categorias_no_incluidas": list(categorias_no_incluidas),
        "deberia_incluir_categoria_en_nombre": deberia_incluir_categoria_en_nombre
    }

    # Resultado final
    return resultado

#input={'dataset_id': 'negocio_20250505_100947_30efecae', 'table_id': 'Negocios'}
#print(compare_business(input))

def compare_business_after_keywords():
    #ver si tienen keywords en sus reseñas
    return

            
"""

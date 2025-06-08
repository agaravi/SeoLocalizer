from typing import List
import statistics
from backend.business.models import Business

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
                    #print(subcat.lower())
                    #print(comp.nombre.lower())
                    if subcat.lower() in comp.nombre.lower():      
                        # Si al menos una categoría aparece en su nombre, y no aparece en el nuestro
                        if not any(subcat.lower() in main_business_name.lower() for subcat in main_business_categories):
                            should_include_category_in_name = True
                            break
                    if subcat not in main_business_categories:
                        print("Categoría no incluida: "+ subcat)
                        categorias_no_incluidas.append(subcat)
            elif isinstance(cat, str):
                #print(cat.lower())
                #print(comp.nombre.lower())
                if cat not in main_business_categories:
                    print("Categoría no incluida: "+ cat)
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
    print("----Negocio principal----")
    if main_business_reviews:
        for review in main_business_reviews:
            for keyword in all_categories:
                #print(keyword)
                if keyword in review:
                    print(keyword + "se encuentra en una review del negocio principal")
                    keywords_in_reviews.append(keyword)
    
    # Verificar inclusión de palabras clave en las reseñas de los competidores
    competitor_reviews=comp.get_translated_reviews()
    excluded_categories = [category for category in all_categories if category not in keywords_in_reviews]
    if competitor_reviews:
        for review in competitor_reviews:
            for keyword in excluded_categories:
                #print(keyword)
                if keyword in review:
                    print(keyword + "se encuentra en la review de un competidor")
                    keywords_in_reviews_competitors.append(keyword)
        

    if main_business.n_fotos is not None:
        all_photos.append(main_business.n_fotos)
    
    if main_business.n_valoraciones is not None:
        all_reviews.append(main_business.n_valoraciones)
    
    # Cálculo de estadísticas
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
    }

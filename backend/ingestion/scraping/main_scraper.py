import time
#from ingestion.scraping.Firmania_scraper import buscar_negocio_firmania
from backend.ingestion.scraping.Zyte_Firmania_scraper import buscar_negocio_firmania
from backend.ingestion.scraping.Zyte_InfoisInfo_scraper import buscar_negocio_infoisinfo
from backend.ingestion.scraping.Zyte_Habitissimo_scraper import buscar_negocio_habitissimo
#from backend.ingestion.scraping.Habitissimo_scraper import buscar_negocio_habitissimo
#from PaginasAmarillas_scraper import buscar_negocio_paginas_amarillas
from backend.ingestion.scraping.Zyte_PaginasAmarillas_scraper import buscar_negocio_paginas_amarillas
#from backend.ingestion.scraping.PaginasAmarillas2_scraper import buscar_negocio_paginas_amarillas2

from backend.ingestion.scraping.normalizations import *

def scrape_local_directories(business_name,city,categoria,province,address):
    # Crea un diccionario
    array={}

    business_name=normalize_name(business_name)

    # Scrapea las fuentes
    firmania=buscar_negocio_firmania(business_name,city,province, address)
    infoisinfo=buscar_negocio_infoisinfo(business_name,city,province,address)
    habitissimo=buscar_negocio_habitissimo(business_name,city,province,address)
    paginas_amarillas=buscar_negocio_paginas_amarillas(business_name,city,province,address)
    #paginas_amarillas2=buscar_negocio_paginas_amarillas2(categoria,negocio,city,province)

    #Guarda los resultados
    array["Firmania"]=firmania
    array["InfoisInfo"]=infoisinfo
    array["Habitissimo"]=habitissimo
    #array["Paginas_Amarillas"]=paginas_amarillas or paginas_amarillas2
    array["Paginas Amarillas"]= paginas_amarillas

    
    print("\n\n[------------------------------RESULTADOS FINALES----------------------------------]\n")
    print(array)
    print(f"El negocio '{business_name}' en '{city}' {'EXISTE' if firmania['Encontrado']=='Si' else 'NO EXISTE'} en Firmania.")
    print(f"El negocio '{business_name}' en '{city}' {'EXISTE' if infoisinfo['Encontrado']=='Si' else 'NO EXISTE'} en InfoisInfo.")
    print(f"El negocio '{business_name}' en '{city}' {'EXISTE' if habitissimo['Encontrado']=='Sí' else 'NO EXISTE'} en Habitissimo.")
    print(f"El negocio '{business_name}' en '{city}' {'EXISTE' if paginas_amarillas['Encontrado']=='Sí' else 'NO EXISTE'} en Páginas Amarillas.")

    consulted_sources=0
    found_sources=0
    name_consistency= True
    locality_consistency=True
    province_consistency=True
    address_consistency=True
    directory_inconsistences=[]
    not_found_sources=[]

    # Comparaciones con la información original para detectar inconsistencias en algunas fuentes
    for directory,values in array.items():
        print(directory)
        print(values)
        if values["Error"] is None:
            consulted_sources+=1
            if values["Encontrado"]=="Si":
                found_sources+=1
                name_consistency= bool(values["Nombre"].lower()==business_name.lower() and name_consistency)
                locality_consistency= bool(values["Localidad"].lower()==city.lower() and locality_consistency)
                province_consistency= bool(values["Provincia"].lower()==province.lower() and province_consistency)
                address_consistency= bool(values["Similaridad_direccion"]>=95.00 and address_consistency)
                if(name_consistency==False or locality_consistency==False or province_consistency==False or address_consistency==False):
                    directory_inconsistences.append(directory)
            elif values["Encontrado"]=="No":
                not_found_sources.append(directory)


    print(f"Fuentes consultadas: {consulted_sources}")
    print(f"Fuentes encontradas: {found_sources}")
    print(f"Consistencia en el nombre: {name_consistency}")
    print(f"Consistencia en la localidad: {locality_consistency}")
    print(f"Consistencia en la provincia: {province_consistency}")
    print(f"Consistencia en la dirección: {address_consistency}")
    print(f"Inconsistencias en: {directory_inconsistences}")
    print(F"No encontrado en{not_found_sources}")


    resultados={
        "consulted_sources":consulted_sources,
        "found_sources":found_sources,
        "name_consistency":name_consistency,
        "locality_consistency":locality_consistency,
        "province_consistency":province_consistency,
        "address_consistency":address_consistency,
        "directory_inconsistences": directory_inconsistences,
        "not_found_sources":not_found_sources
    }
    

    return resultados

#categoria = "Gasolinera"
#nombre = "Gasolinera Repsol"
#city = "Villa del Río"
#provincia="Córdoba"



#categoria = input("Introduce la categoría del negocio (ejemplo: Gasolinera): ")
#nombre = input("Introduce el nombre del negocio (ejemplo: Gasolinera Repsol): ")
#ciudad = input("Introduce la ciudad (ejemplo: Villa del Río): ")
#provincia = input("Introduce la provincia (ejemplo: Córdoba): ")
#direccion = input("Introduce la dirección: ")

"""nombre = "Gestiones Alarife"
ciudad = "Córdoba"
provincia="Córdoba"
direccion="Calle Santas Flora y María, 44 - Local y C/ Mirto, 7, 14012, Córdoba, Córdoba"
categoria="Agencia SEO"

scrape_local_directories(nombre,ciudad,categoria,provincia,direccion)"""
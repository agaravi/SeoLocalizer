import pytest
from backend.ingestion.scraping.normalizations import normalize_name, normalize_address, similarity

def test_normalize_name():
    """
    Comprueba la normalización de nombres de negocios, eliminando sufijos comunes y espacios extra.
    """
    assert normalize_name("Mi Empresa S.L.") == "mi empresa"
    assert normalize_name("  Empresa   ejemplo  ") == "empresa ejemplo"
    assert normalize_name("Empresa, S.A.") == "empresa"
    assert normalize_name("Servicios ABC y Cia.") == "servicios abc" 
    print(f"✅ Test 'test_normalize_name' Passed.")

def test_normalize_address():
    """
    Comprueba la normalización de direcciones, incluyendo la eliminación de tildes, caracteres especiales,
    prefijos de calle comunes y la reordenación.
    """
    assert normalize_address("Calle Mayor, 10, 28001 Madrid") == "10 28001 madrid mayor" 
    assert normalize_address("Plaza de España, 1, 14001 Córdoba") == "1 14001 cordoba de espana" 
    assert normalize_address("Avda. de la Paz, s/n, 41001 Sevilla") == "41001 de la paz sevilla" 
    assert normalize_address("C/ Real n. 5") == "5 real" 
    assert normalize_address("Paseo del Prado, 2, Madrid") == "2 del madrid prado" 
    assert normalize_address("C/ Ingeniero Barbudo") == "barbudo ingeniero" 
    assert normalize_address("Avenida 1ºB de Mayo") == "1b de mayo"
    assert normalize_address("Calle Primero de Marzo") == "1 de marzo"
    print(f"✅ Test 'test_normalize_address' Passed.")

def test_similarity():
    """
    Comprueba el cálculo de similitud entre dos direcciones normalizadas.
    """
    # Casos de alta similitud
    assert similarity("Calle Mayor, 10, Madrid", "C. Mayor, 10, Madrid") >= 90.0 
    assert similarity("Avenida de la Constitución, 1", "Avda. Constitucion, 1") >= 80.0 
    assert similarity("C/ Ingeniero Barbudo", "Ingeniero Barbudo") >= 90.0 

    # Caso de baja similitud
    assert similarity("Calle Falsa, 123", "Otra Calle, 456") < 50.0

    # Casos límite con None
    assert similarity("Calle del Sol, 5", None) == 0
    assert similarity(None, "Calle del Sol, 5") == 0
    assert similarity(None, None) == 0
    print(f"✅ Test 'test_similarity' Passed.")
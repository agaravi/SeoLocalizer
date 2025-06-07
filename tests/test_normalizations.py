import pytest
from backend.ingestion.scraping.normalizations import normalize_name, normalize_address, similarity

def test_normalize_name():
    assert normalize_name("Mi Empresa S.L.") == "mi empresa"
    assert normalize_name("The Best Corp. LTD.") == "best"
    assert normalize_name("  Empresa   ejemplo  ") == "empresa ejemplo"
    assert normalize_name("Empresa, S.A.") == "empresa"
    assert normalize_name("Otra S.A. de C.V.") == "otra" 

def test_normalize_address():
    assert normalize_address("Calle Mayor, 10, 28001 Madrid") == "10 28001 calle mayor madrid"
    assert normalize_address("Plaza de España, 1, 14001 Córdoba") == "1 14001 cordoba de españa plaza"
    assert normalize_address("Avda. de la Paz, s/n, 41001 Sevilla") == "41001 avda de la paz sevilla"
    assert normalize_address("C/ Real n. 5") == "5 c real"
    assert normalize_address("Paseo del Prado, 2, Madrid") == "2 del madrid paseo prado" 
    assert normalize_address("C/ Ingeniero Barbudo") == "barbudo c ingeniero"

def test_similarity():
    assert similarity("Calle Mayor, 10, Madrid", "C. Mayor, 10, Madrid") > 0.9
    assert similarity("Avenida de la Constitución, 1", "Avda. Constitucion, 1") > 0.8
    assert similarity("Calle Falsa, 123", "Otra Calle, 456") < 0.5
    assert similarity("Calle del Sol, 5", "Calle del Sol, 5, Sevilla") > 0.7 
    assert similarity("Calle del Sol, 5", None) == 0
    assert similarity(None, "Calle del Sol, 5") == 0
    assert similarity(None, None) == 0
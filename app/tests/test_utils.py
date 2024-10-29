from app.crawler import normalize_str


def test_normalize_str():
    assert normalize_str("Árboles") == "Arboles"
    assert normalize_str("más") == "mas"
    assert normalize_str("piñata") == "pinata"
    assert normalize_str("Español") == "Espanol"

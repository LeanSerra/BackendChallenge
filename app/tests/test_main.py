def test_query_existing_product(client):
    response = client.get("/product/Product")
    assert response.status_code == 200
    data = response.json()
    print("test")
    for prod in data:
        if prod["id"] == 0:
            assert prod["name"] == "ProductA Name"
        if prod["id"] == 1:
            assert prod["name"] == "ProductB Name"
        else:
            print(f"""prod id = {prod["id"]}""")


def test_query_no_products(client):
    keyword = "non_existing_product"
    response = client.get(f"/product/{keyword}")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No items found with keyword non_existing_product"
    }

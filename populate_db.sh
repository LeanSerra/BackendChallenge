#!/bin/bash

# Define an array of popular supermarket items in Spanish
keywords=(
    "arroz" "aceite" "azúcar" "leche" "huevos" "harina" "pan" "pasta" "café" "té"
    "mantequilla" "queso" "yogur" "pollo" "carne" "pescado" "tomate" "cebolla"
    "papa" "zanahoria" "lechuga" "manzana" "banana" "naranja" "uva" "piña" "sandía"
    "melón" "limón" "fresas" "uva" "pimiento" "ajo" "jengibre" "chocolate" "galletas"
    "cereal" "mermelada" "miel" "sal" "pimienta" "vinagre" "salsa" "mostaza" "mayonesa"
    "ketchup" "fideos" "lentejas" "garbanzos" "frijoles" "arvejas" "maíz" "atún"
    "sardinas" "salmón" "jamón" "salchichas" "panceta" "pescado" "gambas" "aceitunas"
    "champiñones" "avena" "quinoa" "granola" "almendras" "nueces" "pasas" "coco"
    "dulce de leche" "crema" "helado" "tortillas" "nachos" "tacos" "queso rallado"
    "patatas fritas" "palomitas" "empanadas" "pan rallado" "galletitas" "chicle"
    "cacao en polvo" "refresco" "agua mineral" "cerveza" "vino" "whisky" "ron"
    "vodka" "chicha" "zumo" "té helado" "aguacate" "frutillas" "mango" "kiwi"
    "mandarina" "pomelo" "nuez moscada" "canela" "vainilla" "nata" "higos" "dátiles"
    "licor" "jugo" "bebida energética" "champán" "sidra" "azafrán" "romero" "orégano"
    "tomillo" "albahaca" "perejil" "cilantro" "menta" "apio" "col" "brocoli" "coliflor"
    "pepino" "calabacín" "berenjena" "puerro" "espinacas" "almejas" "mejillones"
    "navajas" "langostinos" "calamares" "choclo" "avellanas" "arándanos" "coco rallado"
    "nata para montar" "pan integral" "pan blanco" "pan de molde" "croissants"
    "magdalenas" "muffins" "pizza" "hamburguesa" "perritos calientes" "kebab"
    "sushi" "soja" "tofu" "tempeh" "hummus" "tabulé" "ensalada" "wraps" "burritos"
    "frijoles negros" "tallarines" "ramen" "salsa de soja" "salsa picante"
    "fideos chinos" "salsa de tomate" "pasta de dientes" "champú" "gel de ducha"
    "papel higiénico" "servilletas" "detergente" "jabón" "limpiador" "escoba"
    "bolsas de basura" "esponjas" "cepillo de dientes" "hilo dental" "desodorante"
    "maquillaje" "crema hidratante" "loción" "crema de afeitar" "cuchillas"
    "pañales" "toallitas húmedas" "alcohol en gel" "mascarillas" "gafas de sol"
    "paraguas" "reloj" "bolso" "maleta" "cartera" "monedero" "camisa" "pantalones"
)

# Base URL for the FastAPI endpoint
base_url="http://localhost:8000/product"

# Iterate over each keyword in the list and make a GET request
for keyword in "${keywords[@]}"; do
    # Encode the keyword for the URL
    encoded_keyword=$(echo -n "$keyword" | jq -sRr @uri)

    # Make the curl request
    response=$(curl -s -X 'GET' \
      "$base_url/$encoded_keyword" \
      -H 'accept: application/json')

    echo "Response for $keyword:"
    echo "$response"
    echo "-----------------------------"

    # Small delay to avoid overwhelming the server (optional)
    sleep 0.5
done

import requests

def get_food_nutrition(food_name):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("products"):
        product = data["products"][0]
        nutrients = product.get("nutriments", {})
        return {
            "carbs": nutrients.get("carbohydrates_100g", 0),
            "protein": nutrients.get("proteins_100g", 0),
            "fat": nutrients.get("fat_100g", 0),
            "calories": nutrients.get("energy-kcal_100g", 0),
        }
    return None

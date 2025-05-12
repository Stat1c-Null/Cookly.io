from flask import Blueprint, render_template, request, jsonify
from generateRecipes import get_recipe
from generateRecipes import search_recipes
from pureIngredientDetection import detect_ingredients

views = Blueprint(__name__, "views")

#@views.route("/")
#def home():
#    return render_template("index.html")

@views.route("/submitImage/", methods=["GET", "POST"])
def submitImage():
    if request.method == 'OPTIONS':
        return '', 200  # Respond to preflight
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    print(file)
    #We call the analyzeImage method in food_recognition.py to get the ingredients response as a json
    return jsonify(detect_ingredients(file))

@views.route("/submit/", methods=["GET", "POST"])
def submit():
    if request.method == "GET":
        # Handle GET request logic (if any)
        return jsonify({"message": "GET method for /submit is not implemented"})

    if request.method == "POST":
        calorie_limit = request.form.get('calorieInput')
        protein_intake = request.form.get('proteinInput')
        carb_limit = request.form.get('carbsInput')
        fat_limit = request.form.get('fatsInput')
        number_of_people = request.form.get('peopleInput')
        ingredientsTextBox = request.form.get('ingredientsTextBox')
        allergens = request.form.get('selectedAllergens')
        if request.form.get('other'):
            allergens += ", " + request.form.get("other")

        if "null" in allergens:
            allergens = allergens[0:-6]
        print(number_of_people)
        print(ingredientsTextBox)
        print(f"Calories: {calorie_limit}, Protein: {protein_intake}, Carbs: {carb_limit}, Fats: {fat_limit}, People: {number_of_people}")
        print(f"Allergens: {allergens}")

        return search_recipes(ingredientsTextBox, 1)

@views.route("/fetch_data/", methods= ["GET"])
def fetch_data():
    #Fetch recipe from gemini
    title, ingredients, directions, link = get_recipe()
    if ingredients and directions and title and link:
        # Convert any sets to lists before serializing to JSON
        if isinstance(ingredients, set):
            ingredients = list(ingredients)
        if isinstance(directions, set):
            directions = list(directions)
        return jsonify({"title":title, "ingredients": ingredients, "directions": directions, "link": link})
    return jsonify({"data": None, "message": "Recipe not ready yet, still cooking"})


"""
Lemons, apples, grapes, strawberries, melon, mushrooms, mixed fruit, ham, cheese, pickles, peppers, leeks, cabbage, tomatoes, garlic, oranges,  water,  juice, soup, mustard, various sauces, olives, beer.
"""
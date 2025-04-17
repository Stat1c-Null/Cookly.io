from flask import Blueprint, render_template, request, jsonify
from food_recognition import analyzeImage
from geminiTextRecognition import multiturn_generate_content
from geminiTextRecognition import get_recipe

views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("index.html")

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
    #return jsonify({"success": True, "message": "File received"})
    #We call the analyzeImage method in food_recognition.py to get the ingredients response as a json
    return jsonify(analyzeImage(file))

    #We call the
@views.route("/submit/", methods=["GET", "POST"])
def submit():
    if request.method == "GET":
        # Handle GET request logic (if any)
        return jsonify({"message": "GET method for /submit is not implemented"})

    calorie_limit = request.form.get('calorieInput')
    protein_intake = request.form.get('proteinInput')
    carb_limit = request.form.get('carbsInput')
    fat_limit = request.form.get('fatsInput')
    number_of_people = request.form.get('peopleInput')
    ingredientsTextBox = request.form.get('ingredientsTextBox')
    allergens = request.form.get('selectedAllergens')
    if request.form.get('other'):
        allergens += ", " + request.form.get("other")



    print(f"Calories: {calorie_limit}, Protein: {protein_intake}, Carbs: {carb_limit}, Fats: {fat_limit}, People: {number_of_people}")
    print(f"Allergens: {allergens}")

    #return jsonify({"success": True, "message": "File received"})
    ##if ingredients_image:
    #    ingredients_image.save(f'images/uploadedImage.png')
    #    print(f"Uploaded Image: {ingredients_image.filename}")
    #else:
    #    print("Couldn't upload")

    return multiturn_generate_content(ingredientsTextBox,calorie_limit, protein_intake, carb_limit, fat_limit, number_of_people, allergens)

@views.route("/fetch_data", methods= ["GET"])
def fetch_data():
    #Fetch recipe from gemini
    recipe = get_recipe()
    if recipe:
        return jsonify({"data": recipe})
    return jsonify({"data": None, "message": "Recipe not ready yet, still cooking"})

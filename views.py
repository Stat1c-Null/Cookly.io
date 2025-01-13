from flask import Blueprint, render_template, request, jsonify, flash, session, current_app
from food_recognition import analyzeImage
from geminiTextRecognition import multiturn_generate_content
from geminiTextRecognition import get_recipe

views = Blueprint(__name__, "views")

db = current_app.config.get('DB')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = password

@views.route("/")
def home():
    return render_template("index.html")

@views.route("/submitImage", methods=["GET", "POST"])
def submitImage():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    #We call the analyzeImage method in food_recognition.py to get the ingredients response as a json
    return jsonify(analyzeImage(file))

    #We call the
@views.route("/submit", methods=["GET", "POST"])
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

    print(f"Calories: {calorie_limit}, Protein: {protein_intake}, Carbs: {carb_limit}, Fats: {fat_limit}, People: {number_of_people}")

    ##if ingredients_image:
    #    ingredients_image.save(f'images/uploadedImage.png')
    #    print(f"Uploaded Image: {ingredients_image.filename}")
    #else:
    #    print("Couldn't upload")

    return multiturn_generate_content(ingredientsTextBox,calorie_limit, protein_intake, carb_limit, fat_limit, number_of_people)

@views.route("/fetch_data", methods= ["GET"])
def fetch_data():
    #Fetch recipe from gemini
    recipe = get_recipe()
    if recipe:
        return jsonify({"data": recipe})
    return jsonify({"data": None, "message": "Recipe not ready yet, still cooking"})

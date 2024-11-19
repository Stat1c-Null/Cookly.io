from flask import Blueprint, render_template, request
from food_recognition import generate

views = Blueprint(__name__, "views")


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/submit", methods=["POST"])
def submit():
    calorie_limit = request.form.get('calorieInput')
    protein_intake = request.form.get('proteinInput')
    carb_limit = request.form.get('carbsInput')
    fat_limit = request.form.get('fatsInput')
    number_of_people = request.form.get('peopleInput')
    ingredients_image = request.files.get('ingredientsImage')

    print(f"Calories: {calorie_limit}, Protein: {protein_intake}, Carbs: {carb_limit}, Fats: {fat_limit}, People: {number_of_people}")
    if ingredients_image:
        ingredients_image.save(f'images/uploadedImage.png')
        print(f"Uploaded Image: {ingredients_image.filename}")
    else:
        print("Couldn't upload")

    return generate(calorie_limit, protein_intake, carb_limit, fat_limit, number_of_people, ingredients_image)


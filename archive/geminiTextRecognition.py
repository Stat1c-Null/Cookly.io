import os
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting



textsi_1 = """You will be helping users to create recipes with the stuff they tell you that they have in 
their kitchen or at their disposal, add serving size, calories, fats amount, and protein. When writing the recipe have it like **Meal Name** Name and not on a new line keep it right next to it.
 Format it like **Meal Name:** (Actual Meal Name Here), **Ingredients:** (Actual Ingredient list), **Instructions:** (Actual Instruction list), **Notes:** (Actual notes)"""

recipe_store = {"data": None}


def multiturn_generate_content(ingredients: str, calories: str, protein: str, carbs: str, fat: str, people: str, allergens: list):
    """

    :param ingredients: Full list of ingredients from the image they uploaded
    :param calories: Calories that was sent from the website
    :param protein: Protein that was sent in
    :param carbs: Carbs that was sent in
    :param fat: Fat amount that was sent in
    :param people: Amount of people sent from website
    :return: Gemini's response on what you should make
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gen-lang-client-0415079926-5a7bf175d6bc.json"

    vertexai.init(project="gen-lang-client-0415079926", location="us-central1")

    model = GenerativeModel(
        model_name="gemini-1.5-flash-002",
        system_instruction=textsi_1,
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    # Enable raw responses (use with caution in production)
    chat = model.start_chat(response_validation=False)

    print(ingredients)
    if ingredients == '':
        user_prompt = input("What ingredients do you have today (or type 'exit' to quit)?: ")
    else:
        user_prompt = ingredients

    #base formatting
    assumed_ingredients = "salt, pepper, oil"
    formattedNutrients = format(calories, protein, carbs, fat, people)
    formmatedAllergens = allergens


    #formatting questions to be sent to gemini
    full_prompt = f"What can I cook with: {user_prompt}, {assumed_ingredients}, my allergens are {formmatedAllergens}.Break your response into the following parts:Meal Name,Ingridients,Instructions,Notes.For each section write the name of it at the top"
    start_format = "\nGemini says you should try:\n"
    text = ""

    #Try and get a response from Gemini
    try:
        print(f"Debug: Sending to model -> {full_prompt}")
        response = chat.send_message(full_prompt)
        text = start_format + response.text
        print(start_format + response.text)
        recipe_store["data"] = text
    except Exception as e:
        print(f"An error occurred: {e}")

    return text


def get_recipe():
    print("Sending recipe")
    print(recipe_store.get("data"))
    return recipe_store.get("data")


def format(calories, protein, carbs, fat, people):
    """
    Formats the string in case of empty values
    :param calories:
    :param protein:
    :param carbs:
    :param fat:
    :param people:
    :return:
    """
    formattedNutrients = ""
    if calories is not None and calories != "":
        formattedNutrients += f"under {calories} calories"
    else:
        formattedNutrients += f""
    if protein is not None and protein != "":
        formattedNutrients += f", {protein} protein"
    else:
        formattedNutrients += ""

    if carbs is not None and carbs != "":
        formattedNutrients += f", {carbs} carbs"
    else:
        formattedNutrients += ""

    if fat is not None and fat != "":
        formattedNutrients += f", {fat} fat"
    else:
        formattedNutrients += ""

    if people is not None and people != "":
        if people == "1":
            formattedNutrients += f", for 1 person"
        else:
            formattedNutrients += f", for {people} people"
    else:
        formattedNutrients += ""

    return formattedNutrients


def formatAllergens(allergens: list) -> str:
    s = ""
    for string in allergens:
        s += string + ", "
    if s == "":
        return ""
    else:
        return ", my allergies are " + s


generation_config = {
    "max_output_tokens": 1024,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.OFF
    ),
]

exampleText = """
**Meal Name**

Creamy Ham and Leek Pasta


**Ingredients**

* 100g Pasta (choose a whole wheat variety for added fiber)
* 100g Ham, diced
* 50g Leek, thinly sliced and washed well
* 25g Cheese (e.g., cheddar, Gruyere), grated
* 1 tbsp Butter
* 1/2 cup Milk
* 1 tbsp Sauce (e.g., white sauce, béchamel – you can make a simple one with butter, flour and milk)
* Salt and pepper to taste

**Instructions**

1. Cook the pasta according to package directions.
2. While the pasta cooks, melt the butter in a pan over medium heat. Add the leeks and sauté until softened (about 5 minutes).
3. Stir in the diced ham and cook for another 2-3 minutes.
4. Add the milk and sauce, stirring until combined and slightly thickened.
5. Drain the pasta and add it to the pan with the ham and leek mixture.
6. Stir in the grated cheese until melted and creamy.
7. Season with salt and pepper to taste.


**Notes**

*  This recipe can be easily adapted.  You could add other vegetables from your list (like diced carrots or peppers) to the leek and ham mixture for extra nutrients and flavor.
* For a lower-fat version, use less butter and milk, or substitute some of the milk with vegetable broth.
* To calculate the approximate calories, fat, protein, and carbs you'll need to use a nutrition calculator and input the specific brands and weights of your ingredients.  Nutrient content can vary between brands.  This will give a far more accurate picture than general estimates.  Remember that this recipe is aiming for a healthier, lower calorie version, rather than meeting the unrealistic macro targets initially requested.
"""

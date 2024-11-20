import os
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting

textsi_1 = """You will be helping users to create recipes with the stuff they tell you that they have in their kitchen or at their disposal, add serving size, calories, fats amount, and protein."""

recipe_store = {"data": None}

def multiturn_generate_content(ingredients: str, calories: str, protein: str,carbs: str,fat: str,people: str):
    """

    :param ingredients: Full list of ingredients from the image they uploaded
    :param calories: Calories that was sent from the website
    :param protein: Protein that was sent in
    :param carbs: Carbs that was sent in
    :param fat: Fat amount that was sent in
    :param people: Amount of people sent from website
    :return: Gemini's response on what you should make
    """
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "useful-flame-441821-h0-5e6960a95210.json"

    vertexai.init(project="useful-flame-441821-h0", location="us-central1")

    model = GenerativeModel(
        model_name="gemini-1.5-flash-002",
        system_instruction=textsi_1,
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    # Enable raw responses (use with caution in production)
    chat = model.start_chat(response_validation=False)

    if ingredients == '':
        user_prompt = input("What ingredients do you have today (or type 'exit' to quit)?: ")
    else:
        user_prompt = ingredients

    #base formatting
    assumed_ingredients = "salt, pepper"
    formattedNutrients = f"with only {calories} calories, {protein} protein, {carbs} carbs, {fat} fat, for {people} people"

    #formatting questions to be sent to gemini
    full_prompt = f"What can I make with: {user_prompt}, {assumed_ingredients},  {formattedNutrients}.Break your response into the following parts:Meal Name,Ingridients,Instructions,Notes.For each section write the name of it at the top"
    start_format = "\nGemini says you should try:\n"
    text = ""

    #Try and get a response from Gemini
    try:
        print(f"Debug: Sending to model -> {full_prompt}")
        response = chat.send_message(full_prompt)
        text = start_format+ response.text
        print(start_format + response.text)
        recipe_store["data"] = response.text
    except Exception as e:
        print(f"An error occurred: {e}")

    return text

def get_recipe():
    return recipe_store.get("data")

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


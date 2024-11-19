import os
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting


def multiturn_generate_content(calories: str, protein: str,carbs: str,fat: str,people: str):
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

    while True:
        user_prompt = input("What ingredients do you have today (or type 'exit' to quit)?: ")

        if user_prompt.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break

        assumed_ingredients = "salt, pepper"
        formattedNutrients = f"with only {calories} calories, {protein} protein, {carbs} carbs, {fat} fat, for {people} people"

        full_prompt = f"What can I make with: {user_prompt}, {assumed_ingredients},  {formattedNutrients}"
        start_format = "\nGemini says you should try:\n"

        try:
            print(f"Debug: Sending to model -> {full_prompt}")
            response = chat.send_message(full_prompt)
            print(start_format + response.text)
        except Exception as e:
            print(f"An error occurred: {e}")


textsi_1 = """You will be helping users to create recipes with the stuff they tell you that they have in their kitchen or at their disposal, add serving size, calories, fats amount, and protein."""

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


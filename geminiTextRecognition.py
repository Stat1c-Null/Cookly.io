import base64
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part


def multiturn_generate_content():
    vertexai.init(project="useful-flame-441821-h0", location="us-central1")
    model = GenerativeModel(
        model_name="gemini-1.5-flash-002",
        system_instruction=textsi_1,
        generation_config=generation_config
    )

    chat = model.start_chat()
    userPrompt = ""
    while True:
        user_prompt = input("What ingredients do you have today (or type 'exit' to quit)?: ")

        if user_prompt.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break

        assumed_ingredients = ", salt, pepper, garlic powder, vegetable oil, onion powder"
        start_format = "\nGemini says you should try:\n"

        response = chat.send_message(f"What can I make with: {user_prompt + assumed_ingredients}")
        print(start_format + response.text)


textsi_1 = """You will be helping users to create recipes with the stuff they tell you that they have in their kitchen or disposal."""

generation_config = {
    "max_output_tokens": 8192,
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

multiturn_generate_content()

import base64
import os

import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting


def generate(pathing):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "useful-flame-441821-h0-5e6960a95210.json"

    vertexai.init(project="useful-flame-441821-h0", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        system_instruction=[textsi_1]
    )
    #Takes in the image pathing and where it was located
    with open(pathing, "rb") as img_file:
        image_data = img_file.read()
    #We encode the image
    encoded_image = base64.b64encode(image_data)

    image1 = Part.from_data(
        mime_type="image/png",
        #We Decode the image
        data=base64.b64decode(encoded_image),
    )

    #Needs fine tuning but it should be good after this
    responses = model.generate_content(
        [image1, """What is in this fridge?"""],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    for response in responses:
        print(response.text, end="")

#This could be better but its just what the AI should be doing with the information like context.
textsi_1 = """We only want to find out what ingredients this person has by analyzing what is inside their fridge, pantry, or etc. Just food ingredients and such."""

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

#The image path
image_path = "images/foodinfridge2.png"

#The generated image
generate(image_path)
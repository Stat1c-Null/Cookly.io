import base64
from flask import request
import os
from PIL import Image
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting


#instructions for the AI
textsi_1 = """We only want to find out what ingredients this person has by analyzing what is inside their fridge, 
pantry, or etc. Make it comma separated like: banana, apple, syrup... etc. Listing all the ingredients in their fridge"""
recipe_store = {"data": None}


def analyzeImage(image):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gen-lang-client-0415079926-5a7bf175d6bc.json"

    vertexai.init(project="gen-lang-client-0415079926", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-flash-002",
        system_instruction=[textsi_1]
    )
    #Establishes path name and saves the image
    pathName = "images/uploadedImage.png"
    img = Image.open(image)
    img.save("images/uploadedImage.png")

    with open(pathName, "rb") as imgFile:
        imageData = imgFile.read()


    #We encode the image
    encoded_image = base64.b64encode(imageData)

    image1 = Part.from_data(
        #This is the image type it is analyzing don't change it unless you change the image file type
        mime_type="image/png",
        #We Decode the image
        data=base64.b64decode(encoded_image),
    )

    #Needs fine-tuning but it should be good after this
    responses = model.generate_content(
        [image1, """What is in this fridge?"""],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    #Gemini's image analysis is stored here
    fullResponse = ''
    for response in responses:
        fullResponse += response.text + ""

    #Removes image from our files
    if os.path.exists(pathName):
        os.remove(pathName)
    else:
        print("Unable to remove image")


    print("Full response: " + fullResponse)
    #After generating the ingredients it sees we now send back the data as a json
    return {"data": fullResponse}



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

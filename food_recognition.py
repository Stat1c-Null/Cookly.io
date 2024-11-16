import cv2, deeplake
import numpy as np
import pathlib
import textwrap
import os

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


GEMINI_KEY = os.environ['API_KEY']

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

#https://www.kaggle.com/code/sainikhileshreddy/how-to-use-the-dataset
#Trained model to detect food
"""try:
  #food_model = deeplake.load('hub://sainikhileshreddy/food-recognition-2022-test')
  food_model = hub.load('/kaggle/input/food-recognition-2022/hub/val')
  print("Succesfully loaded Dataset")
except Exception as e:
  print(f"Dataset couldnt be loaded {e}")
  exit()"""

#Load image
img_path = 'images/potatoes.png'
img = cv2.imread(img_path)

if img is None:
  print(f"Could not read image path {img_path}")
  exit()

resized_img = cv2.resize(img, (224, 224))
resized_img = resized_img / 255.0
resized_img = np.expand_dims(resized_img, axis=0)

response = model.generate_content(["Tell me what food is in the picture", resized_img], stream=True)

response.resolve()

cv2.imshow('Food Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

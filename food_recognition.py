import cv2
import deeplake
import numpy as np
import hub
#https://www.kaggle.com/code/sainikhileshreddy/how-to-use-the-dataset
#Trained model to detect food
try:
  #food_model = deeplake.load('hub://sainikhileshreddy/food-recognition-2022-test')
  food_model = hub.load('/kaggle/input/food-recognition-2022/hub/val')
  print("Succesfully loaded Dataset")
except Exception as e:
  print(f"Dataset couldnt be loaded {e}")
  exit()

#Load image
img_path = 'images/potatoes.png'
img = cv2.imread(img_path)

if img is None:
  print(f"Could not read image path {img_path}")
  exit()

resized_img = cv2.resize(img, (224, 224))
resized_img = resized_img / 255.0
resized_img = np.expand_dims(resized_img, axis=0)

try:
    print(food_model.labels)
except Exception as e:
    print(f"Error during inference: {e}")

cv2.imshow('Food Image', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

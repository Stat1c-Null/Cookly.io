import os
import numpy as np
from ultralytics import YOLO
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from roboflow import Roboflow
import yaml
import torch
import requests
import json
from functools import reduce
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API")

#this is our roboflow workspace and project names
WORKSPACE_NAME = "cookly"

#project names - replace with updated realistic one when it finishes uploading
CLEAN_PROJECT_NAME = "food-identifier-68zfx"  # 90k clean dataset
REALISTIC_PROJECT_NAME = "food-realistic-detection"  # 15k realistic dataset <--------------------------------------------REMINDER MIKITA CHANGE THIS TO NAME OF ROBOFLOW DATASET

#these are our dataset versions
CLEAN_VERSION = 1
REALISTIC_VERSION = 3

#training parameters
MODEL_TYPE = "yolov8m"  #change this from medium to small if its takin too long 

#training epochs for each stage
CLEAN_EPOCHS = 30
REALISTIC_EPOCHS = 50

#other parameters
BATCH_SIZE = 16
IMG_SIZE = 640


#ig load a pre-trained model if not training
#you can specify the path to your best model here if we already trained it earlier
MODEL_PATH = "cookly_ingredient_detector/stage2_realistic_dataset/weights/best.pt"

model_to_use = YOLO(MODEL_PATH)

def enhance_image_for_detection(image_path):
    """
    Enhance image contrast and brightness for better object detection.
    
    Args:
        image_path (str): Path to the input image
        
    Returns:
        tuple: (enhanced image array, enhanced image path)
    """
    #first read in the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return None, None
    
    #we create a copy of the original image
    orig_img = img.copy()
    
    #then we convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    #next apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L-channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    #we merge channels and convert back to BGR
    merged = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    
    #then save enhanced image
    enhanced_path = image_path.replace('.jpg', '_enhanced.jpg')
    if image_path == enhanced_path:
        enhanced_path = image_path.replace('.jpg', '_enhanced.jpg')
    cv2.imwrite(enhanced_path, enhanced_img)
    
    return enhanced_img, enhanced_path

def detect_ingredients_multi_scale(model, image_path, conf_threshold=0.2, iou_threshold=0.25, scales=[0.5, 0.75, 1.0, 1.25]):
    """
    Detect ingredients using multi-scale inference.
    Args:
        model (YOLO): Trained YOLOv8 model
        image_path (str): Path to the input image
        conf_threshold (float): Confidence threshold for detections
        iou_threshold (float): IoU threshold for NMS
        scales (list): List of scales for multi-scale inference
    Returns:
        tuple: (image with boxes, list of detected ingredients)
    """
    print(f"Detecting ingredients with multi-scale inference: {image_path}")
    
    #load original image for visualization
    img_for_vis = cv2.imread(image_path)
    if img_for_vis is None:
        print(f"Error: Could not read image at {image_path}")
        return None, []
    
    img_for_vis = cv2.cvtColor(img_for_vis, cv2.COLOR_BGR2RGB)
    
    #also apply image enhancement for better detection
    _, enhanced_path = enhance_image_for_detection(image_path)
    
    #then store all detections from multiple scales and image variants
    all_detections = []
    
    #next process original and enhanced images at multiple scales
    image_variants = [image_path]
    if enhanced_path:
        image_variants.append(enhanced_path)
    
    for img_path in image_variants:
        for scale in scales:
            print(f"Processing {os.path.basename(img_path)} at scale {scale}...")
            
            if scale == 1.0:
                #processes at original scale
                results = model.predict(
                    img_path,
                    conf=conf_threshold,
                    iou=iou_threshold,
                    max_det=50,
                    verbose=False
                )[0]
                
                #adds detections from this scale
                for i in range(len(results.boxes)):
                    box = results.boxes[i]
                    class_id = int(box.cls.item())
                    confidence = float(box.conf.item())
                    class_name = results.names[class_id]
                    bbox = box.xyxy.cpu().numpy()[0].tolist()  # [x1, y1, x2, y2]
                    
                    all_detections.append({
                        'name': class_name,
                        'confidence': confidence,
                        'box': bbox
                    })
            else:
                #read and resize image
                original_img = cv2.imread(img_path)
                if original_img is None:
                    continue
                    
                h, w = original_img.shape[:2]
                new_h, new_w = int(h * scale), int(w * scale)
                resized_img = cv2.resize(original_img, (new_w, new_h))
                
                #save that jawn temporarily
                resized_path = img_path.replace('.jpg', f'_scale_{scale}.jpg')
                if not resized_path.endswith('.jpg'):
                    resized_path = f"{resized_path}_scale_{scale}.jpg"
                cv2.imwrite(resized_path, resized_img)
                
                #process aforementioned jawn
                try:
                    results = model.predict(
                        resized_path,
                        conf=conf_threshold,
                        iou=iou_threshold,
                        max_det=50,
                        verbose=False
                    )[0]
                    
                    #adds detections, rescaling bounding boxes to original image size
                    for i in range(len(results.boxes)):
                        box = results.boxes[i]
                        class_id = int(box.cls.item())
                        confidence = float(box.conf.item())
                        class_name = results.names[class_id]
                        bbox = box.xyxy.cpu().numpy()[0].tolist()
                        
                        #rescale boxes to original image size
                        x1, y1, x2, y2 = bbox
                        x1, x2 = x1/scale, x2/scale
                        y1, y2 = y1/scale, y2/scale
                        
                        all_detections.append({
                            'name': class_name,
                            'confidence': confidence,
                            'box': [x1, y1, x2, y2]
                        })
                except Exception as e:
                    print(f"Error processing resized image: {e}")
                
                #remove temporary file for cleanup
                if os.path.exists(resized_path):
                    os.remove(resized_path)
    
    #remove temporary enhanced image for cleanup
    if enhanced_path and os.path.exists(enhanced_path) and enhanced_path != image_path:
        os.remove(enhanced_path)
    
    #apply non-maximum suppression to remove duplicate detections
    #group detections by class
    class_detections = {}
    for det in all_detections:
        class_name = det['name']
        if class_name not in class_detections:
            class_detections[class_name] = []
        class_detections[class_name].append(det)
    
    #apply NMS for each class
    final_detections = []
    for class_name, detections in class_detections.items():
        #convert to numpy arrays for NMS
        boxes = np.array([det['box'] for det in detections])
        confidences = np.array([det['confidence'] for det in detections])
        
        #apply NMS
        try:
            nms_indices = cv2.dnn.NMSBoxes(
                boxes.tolist(), 
                confidences.tolist(), 
                conf_threshold, 
                iou_threshold
            )
            
            #add non-suppressed detections to final list
            for idx in nms_indices:
                if isinstance(idx, list) or isinstance(idx, np.ndarray):  #for OpenCV < 4.7
                    idx = idx[0]
                final_detections.append(detections[idx])
        except Exception as e:
            print(f"Error applying NMS: {e}")
            #if NMS fails, just use the highest confidence detection for this class
            if detections:
                best_detection = max(detections, key=lambda x: x['confidence'])
                final_detections.append(best_detection)
    
    print(f"Total detections after multi-scale inference and NMS: {len(final_detections)}")
    
    #this draws boxes on image
    for det in final_detections:
        box = det['box']
        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
        
        #then we draw bounding box with blue color
        cv2.rectangle(img_for_vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
        
        #next draw label with background for better visibility
        label = f"{det['name']}: {det['confidence']:.2f}"
        
        #now we calculate text size for background rectangle
        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        
        #this will draw background rectangle for text
        cv2.rectangle(img_for_vis, (x1, y1 - text_height - 10), (x1 + text_width, y1), (0, 0, 255), -1)
        
        #this draws text with white color
        cv2.putText(img_for_vis, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return img_for_vis, final_detections

def format_ingredients_output(detected_ingredients, output_format='csv'):
    """
    Format the detected ingredients list, removing duplicates.
    
    Args:
        detected_ingredients (list): List of detected ingredients
        output_format (str): Output format ('csv', 'array', 'json')
        
    Returns:
        str or list: Formatted output
    """
    #next we remove duplicates by keeping the highest confidence detection for each ingredient
    unique_ingredients = {}
    for ingredient in detected_ingredients:
        name = ingredient['name']
        confidence = ingredient['confidence']
        
        if name not in unique_ingredients or confidence > unique_ingredients[name]['confidence']:
            unique_ingredients[name] = ingredient
    
    #this will get the list of unique ingredient names
    ingredient_names = list(unique_ingredients.keys())
    
    if output_format == 'csv':
        return ', '.join(ingredient_names)
    elif output_format == 'array':
        return ingredient_names
    elif output_format == 'json':
        return unique_ingredients
    else:
        return ingredient_names


def detect_ingredients(img):
    
    #ig load a pre-trained model if not training
    #you can specify the path to your best model here if we already trained it earlier
    MODEL_PATH = "cookly_ingredient_detector/stage2_realistic_dataset/weights/best.pt"

    model_to_use = YOLO(MODEL_PATH)

    img_path = "images/uploadedImage.png"
    img = Image.open(img)
    img.save("images/uploadedImage.png")
    #then run multi-scale detection
    result_img, detections = detect_ingredients_multi_scale(
        model=model_to_use,
        image_path=img_path,
        conf_threshold=0.2,
        iou_threshold=0.25,
        scales=[0.5, 0.75, 1.0, 1.25]
    )
    
    #next we format and print results
    ingredients_csv = format_ingredients_output(detections, 'csv')
    ingredients_array = format_ingredients_output(detections, 'array')
    
    print(f"\nResults for {img_path}:")
    print(f"Detected Ingredients (CSV): {ingredients_csv}")
    print(f"Detected Ingredients (Array): {ingredients_array}")
    
    #Removes image from our files
    if os.path.exists(img_path):
      os.remove(img_path)
    else:
      print("Unable to remove image")

    #After generating the ingredients it sees we now send back the data as a json
    return {"data": ingredients_array}
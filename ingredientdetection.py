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


# diagnostic test methods
def check_roboflow_info(api_key):
    #this will make a GET request to the root endpoint to see workspace info
    url = "https://api.roboflow.com/"
    headers = {"Authorization": f"API_KEY {api_key}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Roboflow account information:")
        print(json.dumps(data, indent=4))
        
        #this shows the actual workspace ID/name and projects
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
# ----- 1. Download and prepare the Roboflow dataset -----

def setup_roboflow_dataset(api_key="uHcB191TBmXa2Jpkrq8K", cookly="food-becxj", FoodIdentifierv1="final-complete-food", version=1):
    """
    this just downloads and sets up the dataset from Roboflow.
    Args:
        api_key (str): Your Roboflow API key
        workspace_name (str): Roboflow workspace name
        project_name (str): Project name
        version (int): Dataset version
    Returns:
        str: Path to the dataset directory
    """
    print("checking roboflow acc info...")
    account_info = check_roboflow_info("uHcB191TBmXa2Jpkrq8K")#try changing to actual key
    if not account_info:
        print("Couldn't retrieve account information. Check your API key.")
        return None
    print(f"Setting up Roboflow dataset: {FoodIdentifierv1}")
    
    rf = Roboflow(api_key="uHcB191TBmXa2Jpkrq8K") #my roboflow api key
    #check which workspace we have access to
    
    workspace_name = "cookly"  
    project_name = "food-identifier-68zfx"  
    version = 1
    
    try:
        workspace = rf.workspace(workspace_name)
        project = workspace.project(project_name)
        print(f"Found project: {project_name}")
        
        dataset = project.version(version).download("yolov8")
        print("Dataset downloaded successfully")
        
        #this is the download method returns the path to the dataset
        dataset_path = os.path.join(os.getcwd(), project_name + "-" + str(version))
        
        print(f"Dataset downloaded to: {dataset_path}")
        return dataset_path
    
    except Exception as e:
        print(f"Error accessing project: {e}")
        
        #we need to list all projects in the workspace to help troubleshooting
        try:
            workspace = rf.workspace(workspace_name)
            projects = workspace.projects()
            print(f"Available projects in workspace '{workspace_name}': {[p.name for p in projects]}")
        except Exception as e2:
            print(f"Error accessing workspace: {e2}")
        
        raise
    
    

# ----- 2. Model Selection and Training Setup -----

def setup_and_train_model(dataset_path, model_type="yolov8n", epochs=50, batch_size=16, img_size=640):
    """
    Setup and train a YOLOv8 model.
    Args:
        dataset_path (str): Path to the dataset directory
        model_type (str): YOLOv8 model size (n, s, m, l, x)
        epochs (int): Number of training epochs
        batch_size (int): Batch size for training
        img_size (int): Image size for training
    Returns:
        YOLO: Trained YOLOv8 model
    """
    print(f"Setting up {model_type} model for training")
    
    #first we load data configuration
    data_yaml = os.path.join(dataset_path, 'data.yaml')
    
    #next need to initialize a pre-trained YOLOv8 model
    model = YOLO(f"{model_type}.pt")
    
    #then we do the train the model part of training the model
    print(f"Starting training for {epochs} epochs")
    model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        patience=10,  # Early stopping patience
        save=True,    # Save checkpoints
        device=0 if torch.cuda.is_available() else 'cpu',
        verbose=True
    )
    
    print("Training complete!")
    return model

# ----- 3. Model Evaluation -----

def evaluate_model(model, dataset_path):
    """
    Evaluate the trained model.
    Args:
        model (YOLO): Trained YOLOv8 model
        dataset_path (str): Path to the dataset directory
    Returns:
        dict: Evaluation metrics
    """
    print("Evaluating model performance")
    
    #replace with path to the validation set
    val_path = os.path.join(dataset_path, 'valid')
    
    #then run validation
    metrics = model.val(data=os.path.join(dataset_path, 'data.yaml'))
    
    print(f"Validation mAP@0.5: {metrics.box.map50:.4f}")#this is Mean Average Precision at IoU threshold 0.5
    print(f"Validation mAP@0.5:0.95: {metrics.box.map:.4f}")#this is Mean Average Precision averaged over IoU thresholds from 0.5 to 0.95
    
    return metrics

# ----- 4. Inference and Visualization -----

def detect_ingredients(model, image_path, conf_threshold=0.05, iou_threshold=0.075):#iou is threshold for non maximum suppression
    """
    Detect ingredients in an image.
    Args:
        model (YOLO): Trained YOLOv8 model
        image_path (str): Path to the input image
        conf_threshold (float): Confidence threshold for detections
        iou_threshold (float): IoU threshold for NMS
    Returns:
        tuple: (image with boxes, list of detected ingredients)
    """
    print(f"Detecting ingredients in: {image_path}")
    
    #this runs inference part
    results = model.predict(
        image_path, 
        conf=conf_threshold,
        iou=iou_threshold,
        max_det=50,  # Maximum number of detections
        verbose=False
    )[0]
    
    #then gets the detected ingredients
    detected_ingredients = []
    for result in results:
        class_id = int(result.boxes.cls.item())
        confidence = float(result.boxes.conf.item())
        class_name = results.names[class_id]
        detected_ingredients.append({
            'name': class_name,
            'confidence': confidence,
            'box': result.boxes.xyxy.cpu().numpy()[0].tolist()  # [x1, y1, x2, y2]
        })
    
    #this part will read image and draw boxes
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    for ingredient in detected_ingredients:
        box = ingredient['box']
        x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
        
        #draws da bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        #draws a label
        label = f"{ingredient['name']}: {ingredient['confidence']:.2f}"
        cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return img, detected_ingredients

def format_ingredients_output(detected_ingredients, output_format='csv'):
    """
    Format the detected ingredients list.
    Args:
        detected_ingredients (list): List of detected ingredients
        output_format (str): Output format ('csv', 'array', 'json')
    Returns:
        str or list: Formatted output
    """
    #this will remove duplicates by keeping the highest confidence detection for each ingredient
    unique_ingredients = {}
    for ingredient in detected_ingredients:
        name = ingredient['name']
        confidence = ingredient['confidence']
        
        if name not in unique_ingredients or confidence > unique_ingredients[name]['confidence']:
            unique_ingredients[name] = ingredient
    
    #this gets the list of unique ingredient names
    ingredient_names = list(unique_ingredients.keys())
    
    if output_format == 'csv':
        return ', '.join(ingredient_names)
    elif output_format == 'array':
        return ingredient_names
    elif output_format == 'json':
        return unique_ingredients
    else:
        return ingredient_names

def visualize_detection(image, detected_ingredients, save_path=None):
    """
    Visualize and optionally save the detection results.
    Args:
        image (numpy.ndarray): Image with bounding boxes
        detected_ingredients (list): List of detected ingredients
        save_path (str, optional): Path to save the visualization
        
    Returns:
        None
    """
    plt.figure(figsize=(12, 10))
    plt.imshow(image)
    plt.title(f"Detected Ingredients: {format_ingredients_output(detected_ingredients, 'csv')}")
    plt.axis('off')
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Visualization saved to: {save_path}")
    
    plt.show()

# ----- 5. Main Function -----

def main():
    """
    Main function to run the ingredient detection pipeline.
    """
    
    ROBOFLOW_API_KEY = "uHcB191TBmXa2Jpkrq8K" 
    
    #this will setup the dataset
    dataset_path = setup_roboflow_dataset(ROBOFLOW_API_KEY)
    
    #these are training parameters
    TRAIN_MODEL = True  
    MODEL_TYPE = "yolov8s"  #Choose from n (nano), s (small), m (medium), l (large), x (xlarge) I SET TO SMALL FOR NOW WE MIGHT WANNA CHANGE THIS LATER -Chris
    EPOCHS = 50
    BATCH_SIZE = 16
    IMG_SIZE = 640
    
    #this is model path (for loading a pre-trained model)
    model_path = "runs/detect/train/weights/best.pt"
    
    if TRAIN_MODEL:
        #first setup and train the model
        model = setup_and_train_model(
            dataset_path=dataset_path,
            model_type=MODEL_TYPE,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            img_size=IMG_SIZE
        )
        
        #call evaluate func the model
        metrics = evaluate_model(model, dataset_path)
    else:
        #load tha pre-trained model
        model = YOLO(model_path)
    
    #this will test the model on sample images
    test_image_path = "C://Users/u/desktop/images/fridge_image.jpg"  #REPLACE WITH YOUR PATH TO THE IMG WHEN RUNNING
    
    #this runs detection
    image, detected_ingredients = detect_ingredients(
        model=model,
        image_path=test_image_path,
        conf_threshold=0.05
    )
    
    #this formats and prints results
    ingredients_csv = format_ingredients_output(detected_ingredients, 'csv')
    ingredients_array = format_ingredients_output(detected_ingredients, 'array')
    
    print(f"Detected Ingredients (CSV): {ingredients_csv}")
    print(f"Detected Ingredients (Array): {ingredients_array}")
    
    #then we need to visualize the results
    visualize_detection(
        image=image,
        detected_ingredients=detected_ingredients,
        save_path="ingredient_detection_result.jpg"
    )

if __name__ == "__main__":
    main()

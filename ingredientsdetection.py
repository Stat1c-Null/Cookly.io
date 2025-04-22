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

# ----- Helper Functions -----

def check_roboflow_info(api_key):
    """
    Check Roboflow account information and available workspaces/projects.
    
    Args:
        api_key (str): Roboflow API key
        
    Returns:
        dict: Account information
    """
    url = "https://api.roboflow.com/"
    headers = {"Authorization": f"API_KEY {api_key}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Roboflow account information:")
        print(json.dumps(data, indent=4))
        return data
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def list_workspace_projects(rf, workspace_name):
    """
    List all projects in a Roboflow workspace.
    
    Args:
        rf (Roboflow): Roboflow instance
        workspace_name (str): Workspace name
        
    Returns:
        list: Available projects
    """
    try:
        workspace = rf.workspace(workspace_name)
        projects = workspace.projects()
        project_names = [p.name for p in projects]
        print(f"Available projects in workspace '{workspace_name}': {project_names}")
        return projects
    except Exception as e:
        print(f"Error accessing workspace: {e}")
        return []

# ----- 1. First we download and prepare the Roboflow datasets -----

def setup_roboflow_datasets(api_key, workspace_name, clean_project_name, realistic_project_name, 
                           clean_version=1, realistic_version=1):
    """
    Download and set up both clean and realistic datasets from Roboflow.
    Args:
        api_key (str): Roboflow API key
        workspace_name (str): Workspace name (e.g., "cookly")
        clean_project_name (str): Name of the 90k clean dataset project
        realistic_project_name (str): Name of the 15k realistic dataset project
        clean_version (int): Version of the clean dataset
        realistic_version (int): Version of the realistic dataset
    Returns:
        tuple: (clean_dataset_path, realistic_dataset_path)
    """
    print("Checking Roboflow account information...")
    account_info = check_roboflow_info(api_key)
    if not account_info:
        print("Couldn't retrieve account information. Check your API key.")
        return None, None
    
    rf = Roboflow(api_key=api_key)
    
    #this lists all available projects
    list_workspace_projects(rf, workspace_name)
    
    #download clean dataset
    clean_dataset_path = None
    """try:
        print(f"Setting up clean dataset: {clean_project_name} (version {clean_version})")
        workspace = rf.workspace(workspace_name)
        project = workspace.project(clean_project_name)
        print(f"Found project: {clean_project_name}")
        
        clean_dataset = project.version(clean_version).download("yolov8")
        clean_dataset_path = os.path.join(os.getcwd(), clean_project_name + "-" + str(clean_version))
        print(f"Clean dataset downloaded to: {clean_dataset_path}")
    except Exception as e:
        print(f"Error downloading clean dataset: {e}")"""
    
    #then we download realistic dataset
    realistic_dataset_path = None
    try:
        print(f"Setting up realistic dataset: {realistic_project_name} (version {realistic_version})")
        workspace = rf.workspace(workspace_name)
        project = workspace.project(realistic_project_name)
        print(f"Found project: {realistic_project_name}")
        
        realistic_dataset = project.version(realistic_version).download("yolov8")
        realistic_dataset_path = os.path.join(os.getcwd(), realistic_project_name + "-" + str(realistic_version))
        print(f"Realistic dataset downloaded to: {realistic_dataset_path}")
    except Exception as e:
        print(f"Error downloading realistic dataset: {e}")
        print("The realistic dataset may still be processing on Roboflow. You can continue with the clean dataset for now.")
    
    return clean_dataset_path, realistic_dataset_path

# ----- 2. Model Training Part -----

def train_model(dataset_path, model_type="yolov8m", epochs=50, batch_size=16, img_size=640, 
               pretrained_weights=None, project_name="ingredient_detector", run_name=None):
    """
    Train a YOLOv8 model on a dataset.
    
    Args:
        dataset_path (str): Path to the dataset directory
        model_type (str): YOLOv8 model size (n, s, m, l, x)
        epochs (int): Number of training epochs
        batch_size (int): Batch size for training
        img_size (int): Image size for training
        pretrained_weights (str, optional): Path to pretrained weights
        project_name (str): Project name for saving results
        run_name (str, optional): Run name for saving results
        
    Returns:
        YOLO: Trained YOLOv8 model
    """
    print(f"Setting up {model_type} model for training")
    
    #we load data configuration
    data_yaml = os.path.join(dataset_path, 'data.yaml')
    
    #then we init model
    if pretrained_weights:
        print(f"Loading pretrained weights from: {pretrained_weights}")
        model = YOLO(pretrained_weights)
    else:
        print(f"Initializing model with default {model_type} weights")
        model = YOLO(f"{model_type}.pt")
    
    #need to set up run name if not provided
    if run_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"train_{timestamp}"
    
    #next train the model
    print(f"Starting training for {epochs} epochs")
    model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch_size,
        imgsz=img_size,
        patience=15,  #early stopping patience
        save=True,    #save checkpoints
        device=0 if torch.cuda.is_available() else 'cpu',
        verbose=True,
        augment=True,  #enables augmentation
        project=project_name,
        name=run_name,
        #below is our different augmentation parameters    <---------------------------------also check make sure these are right before running
        mosaic=1.0,    #enables mosaic augmentation
        mixup=0.3,     #enables mixup augmentation
        degrees=30.0,  #rotation augmentation
        translate=0.2, #translation augmentation
        scale=0.5,     #scale augmentation
        shear=10.0,    #shear augmentation
        perspective=0.001,  #perspective augmentation
        flipud=0.5,    #vertical flip
        fliplr=0.5,    #horizontal flip
        hsv_h=0.2,     #HSV hue augmentation
        hsv_s=0.7,     #HSV saturation augmentation
        hsv_v=0.4,     #HSV value augmentation
        copy_paste=0.3,  #Copy-paste augmentation
    )
    
    print(f"Training complete! Model saved to {os.path.join(project_name, run_name)}")
    return model

# ----- 3. Two-Stage Training Pipeline -----

def two_stage_training(clean_dataset_path, realistic_dataset_path, model_type="yolov8m",
                      clean_epochs=30, realistic_epochs=50, batch_size=16, img_size=640):   #<-------------------------------- maybe change number of epochs if training too slowly
    """
    Implement the two-stage training pipeline:
    1. Train on clean dataset
    2. Fine-tune on realistic dataset
    Args:
        clean_dataset_path (str): Path to the clean dataset
        realistic_dataset_path (str): Path to the realistic dataset
        model_type (str): YOLOv8 model size
        clean_epochs (int): Epochs for clean dataset training
        realistic_epochs (int): Epochs for realistic dataset fine-tuning
        batch_size (int): Batch size
        img_size (int): Image size
    Returns:
        tuple: (first_stage_model, final_model)
    """
    #first we create project directory
    project_dir = "cookly_ingredient_detector"
    os.makedirs(project_dir, exist_ok=True)
    
    #Stage 1: Train on clean dataset
    """print("\n===== STAGE 1: TRAINING ON CLEAN DATASET =====")
    first_stage_model = train_model(
        dataset_path=clean_dataset_path,
        model_type=model_type,
        epochs=clean_epochs,
        batch_size=batch_size,
        img_size=img_size,
        project_name=project_dir,
        run_name="stage1_clean_dataset"
    )
    
    #we need to evaluate on clean dataset
    print("\nEvaluating first stage model on clean dataset validation set")
    clean_metrics = first_stage_model.val(data=os.path.join(clean_dataset_path, 'data.yaml'))
    print(f"Clean dataset mAP@0.5: {clean_metrics.box.map50:.4f}")
    print(f"Clean dataset mAP@0.5:0.95: {clean_metrics.box.map:.4f}")
    
    #then get path to best weights from first stage
    first_stage_weights = os.path.join(project_dir, "stage1_clean_dataset", "weights", "best.pt")
    
    #ifff realistic dataset is not available yet, return the first stage model (i wrote this part while it was still uploading to roboflow, made sense at the time whatever)
    if not realistic_dataset_path:
        print("\nRealistic dataset not available yet. Returning first stage model.")
        print(f"When the realistic dataset is ready, you can continue training by loading weights from: {first_stage_weights}")
        return first_stage_model, None
    """
    first_stage_weights = "weights_stage1/best.pt"
    first_stage_model = None
    #Stage 2: Fine-tune on realistic dataset
    print("\n===== STAGE 2: FINE-TUNING ON REALISTIC DATASET =====")
    final_model = train_model(
        dataset_path=realistic_dataset_path,
        pretrained_weights=first_stage_weights,
        epochs=realistic_epochs,
        batch_size=batch_size,
        img_size=img_size,
        project_name=project_dir,
        run_name="stage2_realistic_dataset"
    )
    
    #then we evaluate on realistic dataset
    print("\nEvaluating final model on realistic dataset validation set")
    realistic_metrics = final_model.val(data=os.path.join(realistic_dataset_path, 'data.yaml'))
    print(f"Realistic dataset mAP@0.5: {realistic_metrics.box.map50:.4f}")
    print(f"Realistic dataset mAP@0.5:0.95: {realistic_metrics.box.map:.4f}")
    
    # Also evaluate on clean dataset to check for performance degradation
    print("\nEvaluating final model on clean dataset validation set")
    clean_metrics_final = final_model.val(data=os.path.join(clean_dataset_path, 'data.yaml'))
    print(f"Clean dataset mAP@0.5: {clean_metrics_final.box.map50:.4f}")
    print(f"Clean dataset mAP@0.5:0.95: {clean_metrics_final.box.map:.4f}")
    #i know im doing this ^^^ twice but I'm doing it first before we train on the second datset and then again after we train on the second datset to make sure it doesn't get worse,
    #and if it does it'll output the first stage model as well so we can use that
    return first_stage_model, final_model

# ----- 4. Image Enhancement for Better Detection -----

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

# ----- 5. Inference Functions -----

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
    if image is None:
        print("Error: Cannot visualize a None image")
        return
        #sometimes i just be adding comments for fun tbh ion even really got shit to say
    plt.figure(figsize=(12, 10))
    plt.imshow(image)
    plt.title(f"Detected Ingredients: {format_ingredients_output(detected_ingredients, 'csv')}")
    plt.axis('off')
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Visualization saved to: {save_path}")
    
    plt.show()

# ----- 6. Main Function -----

def main():
    """
    Main function to run the ingredient detection pipeline.
    """
    
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
    TRAIN_MODEL = False
    MODEL_TYPE = "yolov8m"  #change this from medium to small if its takin too long 
    
    #training epochs for each stage
    CLEAN_EPOCHS = 30
    REALISTIC_EPOCHS = 50
    
    #other parameters
    BATCH_SIZE = 16
    IMG_SIZE = 640
    DOWNLOAD_DATASET = False

    if DOWNLOAD_DATASET:
      #this just sets up the datasets
      clean_dataset_path, realistic_dataset_path = setup_roboflow_datasets(
          api_key=ROBOFLOW_API_KEY,
          workspace_name=WORKSPACE_NAME,
          clean_project_name=CLEAN_PROJECT_NAME,
          realistic_project_name=REALISTIC_PROJECT_NAME,
          clean_version=CLEAN_VERSION,
          realistic_version=REALISTIC_VERSION
      )
    
      """if not clean_dataset_path:
          print("Error: Failed to set up the clean dataset. Please check your Roboflow settings.")
          return"""
      
      #if our realistic dataset isn't ready yet, provide instructions for later
      if not realistic_dataset_path:
          print("\nThe realistic dataset may still be processing on Roboflow.")
          print("You can continue with training on the clean dataset for now.")
          print("Once the realistic dataset is ready, you can set REALISTIC_DATASET_READY = True and run again.")
    
    if TRAIN_MODEL:
        #this will run the two-stage training
        first_stage_model, final_model = two_stage_training(
            clean_dataset_path=clean_dataset_path,
            realistic_dataset_path=realistic_dataset_path,
            model_type=MODEL_TYPE,
            clean_epochs=CLEAN_EPOCHS,
            realistic_epochs=REALISTIC_EPOCHS,
            batch_size=BATCH_SIZE,
            img_size=IMG_SIZE
        )
        
        #then we use the best available model for testing
        model_to_use = final_model if final_model else first_stage_model
    else:
        #ig load a pre-trained model if not training
        #you can specify the path to your best model here if we already trained it earlier
        MODEL_PATH = "cookly_ingredient_detector/stage2_realistic_dataset/weights/best.pt"
        
        if not os.path.exists(MODEL_PATH):
            print(f"Error: Pre-trained model not found at {MODEL_PATH}")
            print("Please train the model first or provide the correct path.")
            return
        
        model_to_use = YOLO(MODEL_PATH)
    
    #test the model on a sample image
    print("\n===== TESTING MODEL ON SAMPLE IMAGES =====")
    
    #then replace with your test image paths <---------------------------------------------------reminder to change this when testing
    test_images = [
        "test_images/image1.jpg",
        "test_images/image2.jpg",
        "test_images/image3.jpg",
        "test_images/image4.jpg",
        #add more test images as needed
    ]
    
    #this will loop through test images
    for img_path in test_images:
        if not os.path.exists(img_path):
            print(f"Warning: Test image not found at {img_path}, skipping...")
            continue
        
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
        
        #then visualize and save results
        save_path = f"results_{os.path.basename(img_path)}"
        visualize_detection(
            image=result_img,
            detected_ingredients=detections,
            save_path=save_path
        )

if __name__ == "__main__":
    main()
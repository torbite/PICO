from ultralytics import YOLO
from mss import mss
import numpy as np
import cv2
import pyautogui as gui
import pytesseract
import copy
import os
import time
import torch

# pytesseract.pytesseract.tesseract_cmd = os.path.join(os.getcwd(), "tesseract/windows", "tesseract.exe")


proportions = ()
def getScreenProportions():
    """This function takes the screen size and the gui size and returns the proportions of the screen"""
    sct = mss()

    screen = sct.grab(sct.monitors[1])
    image = np.array(screen)
    image = cv2.cvtColor(np.array(screen), cv2.COLOR_BGRA2BGR)
    
    proportion_x = gui.size().width/image.shape[1]
    proportion_y = gui.size().height/image.shape[0]

    return (proportion_x, proportion_y)
proportions = getScreenProportions()
models = {}
def load_all_models(models_dir="../../yoloModels"):
    """Preload all YOLO models from the given directory into the models dict."""
    for folder in os.listdir(models_dir):
        model_path = os.path.join(models_dir, folder, "mainModel.pt")
        if os.path.isfile(model_path):
            print(f"Loading model: {folder}")
            models[folder.lower()] = YOLO(model_path)
    print(f"Loaded {len(models)} models.")

# Call this once at startup
load_all_models()
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
print(DEVICE)

# one-time: warmup (avoids first-call penalty)
for m in models.values():
    m.to(DEVICE)
    _ = m.predict(source=np.zeros((640,640,3), dtype=np.uint8), imgsz=640, device=DEVICE, verbose=False)

def getCurrentScreenImage():
    """This function takes a screenshot of the current screen and returns it as a numpy array that's already converted to BGR"""
    sct = mss()
    screen = sct.grab(sct.monitors[1])
    image = np.array(screen)
    image = cv2.cvtColor(np.array(screen), cv2.COLOR_BGRA2BGR)
    return image

def getModelPrediction(app_name : str, imagex : np.array, grayscale : bool = True):
    """This function takes the ai model and the image and returns the predictions of the model"""
    global models
    image = copy.deepcopy(imagex)
    if len(image.shape) == 2:  # grayscale with shape (H, W)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    
    if grayscale:
        if len(image.shape) == 3 and image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    app_name = app_name.lower()
    if app_name != "find_app" and app_name != "separate_text":
        find_preds = getModelPrediction("find_app", image, True)
        # print(find_preds)
        if app_name not in find_preds.keys():
            print(f"App '{app_name}' not found in predictions.")
            raise KeyError(f"App '{app_name}' not found in predictions.")

        app_area = find_preds[app_name][0]
        x1, y1 = app_area[0]
        x2, y2 = app_area[1]

        # Create a black image
        masked = np.zeros_like(image)

        # Copy only the app area from original image
        if len(image.shape) == 2:
            masked[y1:y2, x1:x2] = image[y1:y2, x1:x2]  # grayscale
        else:
            masked[y1:y2, x1:x2, :] = image[y1:y2, x1:x2, :]  # color

        image = masked
    
    if len(image.shape) == 2:  # grayscale with shape (H, W)
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
    model = models[app_name]
    results = model.predict(source=copy.deepcopy(image), save=False, conf=0.25, verbose=False)

    objects = {}

    r = results[0]
    for box in r.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        conf = box.conf[0].item()
        class_id = int(box.cls[0].item())
        label = r.names[class_id]

        if label not in objects.keys():
            objects[label] = []
        objects[label].append(((x1,y1),(x2,y2)))

    objects = {k.lower(): v for k, v in objects.items()}
    return objects

def getMiddlePosition(rectangle_array):
    """This function takes the coordinates of a rectangle and returns the middle point of it"""
    
    x_ = (rectangle_array[0][0] + rectangle_array[1][0])/2
    y_ = (rectangle_array[0][1] + rectangle_array[1][1])/2

    middle_point = (x_, y_)

    return middle_point

def getCroppedImage(imagex, element_boundaries):
    """This function takes the image and the element boundaries and returns the cropped image"""
    image = copy.deepcopy(imagex)
    x1,y1 = element_boundaries[0]
    x2,y2 = element_boundaries[1]
    # print(y1, y2)
    croppedImage = image[y1:y2, x1:x2]
    return croppedImage

def getTextFromCroppedImage(image):
    """This fucntions takes a alreadt croped image and uses pytesseract with the trained AI to get the text from it"""
    # croppedImage = getCroppedImage(image, element_boundaries)

    result : dict = getModelPrediction("separate_text",  image)


    if result.keys() is None:
        return "no text found"
    textsDict = {}
    for key in result.keys():
        textsDict[key] = []
        for element in result[key]:
            textSection = getCroppedImage(image, element)
            text = pytesseract.image_to_string(textSection)
            textList = list(text)
            rm = 0
            for i in range(len(textList)):
                if textList[i] == "\n":
                    rm += 1

            for i in range(rm):
                textList.remove("\n")
                
            finall = "".join(textList)
            textsDict[key].append(finall)

    return textsDict

def getTextFromImage(image, elements):
    result = {}
    for key in elements.keys():
        result[key] = []
        for element in elements[key]:
            if isinstance(element[1], str):
                text = element[1]
                result[key].append((element, text))
                continue
            textSection = getCroppedImage(image, element)
            textsDict = getTextFromCroppedImage(textSection)
            if "main_text" not in textsDict.keys():
                text = ""
                result[key].append((element, text))
                continue
            text = textsDict["main_text"][0]
            result[key].append((element, text))
    return result
            
def saveImage(imagex, name, elements):
    """This function takes an image and a name and saves the image with the name with the rectangles and text"""
    green_color = (0, 255, 0)
    image = copy.deepcopy(imagex)
    for key in elements.keys():
        for element in elements[key]:
            cv2.rectangle(image, (element[0][0], element[0][1]), (element[1][0], element[1][1]), color=green_color, thickness=5)
            text = f"{key}"
            cv2.putText(image, text, (element[0][0], element[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=green_color, thickness=2)

    cv2.imwrite(f"{name}.png", image)
    return None

def getAppElements(AppName: str = "", withText:bool= False, grayscale: bool = True, return_image: bool = False):
    """
    Take a screenshot and run the YOLO model for AppName.
    Returns:
        preds (dict)                    — label -> [((x1,y1),(x2,y2)), ...]
        image (np.ndarray, optional)    — BGR screenshot if return_image=True
    """
    global models

    if AppName not in models.keys():
        return
    
    img = getCurrentScreenImage()
    try:
        preds = getModelPrediction(AppName.lower(), img, grayscale=grayscale)
    except KeyError as e:
        # Raised when 'find_app' doesn't detect WhatsApp on the screen
        print(str(e))
        preds = {}

    if withText:
        preds = getTextFromImage(img, preds)
        

    if return_image:
        return preds, img
    return preds


################################################################################################
                                    #COMPUTER ACTIONS#
################################################################################################

def clickOnElement(element):
    """This function takes a tuple with the coordinates of the element and clicks on it"""
    global proportions
    # proportions = proportions

    if isinstance(element[1], str):
        element = element[0]
    middle_point = getMiddlePosition(element)
    x_fake = middle_point[0]
    y_fake = middle_point[1]
    x = x_fake * proportions[0]
    y = y_fake * proportions[1]
    gui.click(x, y)
    # time.sleep(0.2)
    gui.click(x, y)
    # time.sleep(0.5)
    return None

################################################################################################

################################################################################################


# backend.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import cv2 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

OOD_THRESHOLD = 0.5          
MAIN_MODEL_THRESHOLD = 0.1    

MODEL_PATH = "global_model.keras"     
OOD_MODEL_PATH = "ood_model.h5"      
CLASS_NAMES = ["ballooning", "fibrosis", "inflammation", "steatosis"]

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Main diagnosis model loaded successfully.")
except Exception as e:
    print("Error loading main diagnosis model:", e)

try:
    ood_model = tf.keras.models.load_model(OOD_MODEL_PATH)
    print("OOD classifier loaded successfully.")
except Exception as e:
    print("Error loading OOD classifier model:", e)

def preprocess_image(image: Image.Image):
    """
    Resize, normalize, and expand dimensions of the image for prediction.
    """
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

def contains_face(image: Image.Image) -> bool:
    """
    Detects faces using OpenCV's Haar cascades.
    """
    try:
        open_cv_image = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
        face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        return len(faces) > 0
    except Exception as e:
        print("Error in face detection:", e)
        return False

def is_valid_histopathology(image: Image.Image) -> bool:
    """
    Uses the OOD classifier to determine whether the given image is a valid histopathological slide.
    Returns True if valid (probability >= OOD_THRESHOLD), otherwise False.
    """
    try:
        preprocessed = preprocess_image(image)
        prob_valid = ood_model.predict(preprocessed)[0][0]
        print("OOD prediction (validity probability):", prob_valid)
        return prob_valid >= OOD_THRESHOLD
    except Exception as e:
        print("Error in OOD validation:", e)
        raise e 

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    
    contents = await file.read()
    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        print("Error reading image:", e)
        return JSONResponse(
            content={"error": f"Failed to read image: {e}"},
            status_code=400
        )

    if contains_face(image):
        print("Image rejected due to face detection.")
        return JSONResponse(
            content={"error": "The uploaded image appears to contain a face. Please upload an appropriate liver histopathology slide."},
            status_code=400
        )

    try:
        input_tensor = preprocess_image(image)
    except Exception as e:
        print("Error in image preprocessing:", e)
        return JSONResponse(
            content={"error": f"Image preprocessing failed: {e}"},
            status_code=400
        )

    try:
        prob_valid = ood_model.predict(input_tensor)[0][0]
        print("OOD prediction (validity probability):", prob_valid)
        if prob_valid < OOD_THRESHOLD:
            print("Image rejected by OOD classifier.")
            return JSONResponse(
                content={"error": "The uploaded image does not appear to be a valid histopathological slide (OOD probability too low)."},
                status_code=400
            )
    except Exception as e:
        print("Exception during OOD prediction:", e)
        return JSONResponse(
            content={"error": f"OOD classifier error: {e}"},
            status_code=500
        )

    try:
        predictions = model.predict(input_tensor)
        predicted_prob = np.max(predictions)
        print("Main model confidence:", predicted_prob)
    except Exception as e:
        print("Exception during main model prediction:", e)
        return JSONResponse(
            content={"error": f"Main model prediction error: {e}"},
            status_code=500
        )

    print("Predictions array:", predictions)
    
    if predicted_prob < MAIN_MODEL_THRESHOLD:
        print("Image rejected due to insufficient main model confidence.")
        return JSONResponse(
            content={"error": "The image was not recognized with sufficient diagnostic confidence. Please ensure the image is clear and try again."},
            status_code=400
        )

    predicted_class = CLASS_NAMES[np.argmax(predictions)]
    confidence = float(predicted_prob * 100)
    print("Image accepted. Predicted class:", predicted_class, "with confidence:", confidence)
    
    return JSONResponse(content={"predicted_class": predicted_class, "confidence": confidence})

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
